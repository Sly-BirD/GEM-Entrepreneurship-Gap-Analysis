import pandas as pd
import numpy as np


def load_and_clean():
    tea_raw = pd.read_csv("TEA_by_gender.csv")
    pc_raw = pd.read_csv("Perceived_capabilities_by_gender.csv")
    fear_raw = pd.read_csv("Fear_of_failure_by_gender.csv")

    # The uploaded CSVs use Women_Rate (%), Men_Rate (%), W_M_Ratio; add Year=2023
    def reshape(df: pd.DataFrame, female_col: str, male_col: str, out_female: str, out_male: str) -> pd.DataFrame:
        df = df.copy()
        df = df.rename(columns={"Country": "Country", female_col: out_female, male_col: out_male})
        # Drop aggregates and region/income rows
        drop_names = {
            "Sample Average",
            "Central and East Asia",
            "Europe & UK",
            "Latin America and Caribbean",
            "Middle East and Africa",
            "North America",
            "High Income",
            "Middle Income",
            "Low Income",
        }
        df = df[~df["Country"].isin(drop_names)].copy()
        # Coerce numerics
        def numify(s):
            return (s.astype(str)
                     .str.replace('%', '', regex=False)
                     .str.replace(',', '', regex=False)
                     .str.replace('\u2212', '-', regex=False)
                     .str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
                     .astype(float))
        df[out_female] = numify(df[out_female])
        df[out_male] = numify(df[out_male])
        df["Country"] = df["Country"].astype(str).str.strip()
        df["Year"] = 2023
        return df[["Country", "Year", out_female, out_male]]

    tea = reshape(tea_raw, "Women_Rate (%)", "Men_Rate (%)", "Female TEA", "Male TEA")
    pc = reshape(pc_raw, "Women_Rate (%)", "Men_Rate (%)", "PerceivedCapability_Female", "PerceivedCapability_Male")
    fear = reshape(fear_raw, "Women_Rate (%)", "Men_Rate (%)", "FearOfFailure_Female", "FearOfFailure_Male")

    # Strip and coerce numerics
    def numify(s):
        return (s.astype(str)
                 .str.replace('%', '', regex=False)
                 .str.replace(',', '', regex=False)
                 .str.replace('\u2212', '-', regex=False)
                 .str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
                 .astype(float))

    # Ensure types
    for df in [tea, pc, fear]:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Merge
    df = tea.merge(pc, on=["Country", "Year"], how="inner")
    df = df.merge(fear, on=["Country", "Year"], how="inner")

    # Keep complete rows
    required = [
        "Female TEA", "Male TEA",
        "PerceivedCapability_Female", "PerceivedCapability_Male",
        "FearOfFailure_Female", "FearOfFailure_Male",
    ]
    df = df.dropna(subset=["Country", "Year"] + required).copy()
    df = df.sort_values(["Year", "Country"]).reset_index(drop=True)
    return df


def run_regression_numpy(df: pd.DataFrame) -> dict:
    data = df.copy()
    data["FemaleGap"] = data["Female TEA"] - data["Male TEA"]
    X = data[["FearOfFailure_Female", "PerceivedCapability_Female"]].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = data["FemaleGap"].to_numpy(dtype=float)
    mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    X = X[mask]
    y = y[mask]
    n, k = X.shape
    if n <= k:
        raise ValueError("Not enough observations for regression.")
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    resid = y - y_hat
    sse = float((resid ** 2).sum())
    sst = float(((y - y.mean()) ** 2).sum())
    sigma2 = sse / (n - k)
    XtX_inv = np.linalg.inv(X.T @ X)
    var_beta = sigma2 * XtX_inv
    se_beta = np.sqrt(np.diag(var_beta))
    r2 = 1.0 - (sse / sst) if sst > 0 else np.nan
    return {
        "coef": beta,
        "se": se_beta,
        "r2": r2,
        "n": n,
        "k": k,
        "names": ["const", "FearOfFailure_Female", "PerceivedCapability_Female"],
    }


def main():
    df = load_and_clean()
    df["FemaleGap"] = df["Female TEA"] - df["Male TEA"]

    # Preview
    print("CSV Preview (first 5 rows):")
    print(df.head(5).to_csv(index=False))

    # Full CSV
    print("Full CSV:")
    print(df.to_csv(index=False))

    # Regression
    print("Regression Summary:")
    res = run_regression_numpy(df)
    print("Variable,Coef,StdErr")
    for name, b, se in zip(res["names"], res["coef"], res["se"]):
        print(f"{name},{b:.6f},{se:.6f}")
    print(f"R-squared: {res['r2']:.4f}")

    coef_map = dict(zip(res["names"], res["coef"]))
    fear_sign = "decreases" if coef_map.get("FearOfFailure_Female", 0.0) < 0 else "increases"
    cap_sign = "decreases" if coef_map.get("PerceivedCapability_Female", 0.0) < 0 else "increases"
    print("Interpretation:")
    print(
        f"Holding the other factor constant, a higher female fear of failure {fear_sign} the female TEA gap. "
        f"Higher female perceived capabilities {cap_sign} the female TEA gap. "
        f"See coefficients and R-squared above for magnitude and fit."
    )


if __name__ == "__main__":
    main()


