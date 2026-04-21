from huggingface_hub import HfApi
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import datetime
import os

# 用户配置
HF_USERNAME = "YDXX"
README_PATH = "README.md"
MODEL_LOG_FILE = "other/log_model_download.txt"
DATASET_LOG_FILE = "other/log_dataset_download.txt"
PLOT_FILE = "other/hf_downloads_chart.png"


def _format_thousands(value, _):
    return f"{int(value):,}"

def get_hf_downloads(username):
    api = HfApi()
    models = api.list_models(author=username)
    datasets = api.list_datasets(author=username)

    model_downloads = sum(m.downloads for m in models)
    dataset_downloads = sum(d.downloads for d in datasets)

    return model_downloads, dataset_downloads

def log_downloads(model_downloads, dataset_downloads):
    today = datetime.date.today().strftime("%Y-%m-%d")
    with open(MODEL_LOG_FILE, "a") as f:
        f.write(f"{today},{model_downloads}\n")
    with open(DATASET_LOG_FILE, "a") as f:
        f.write(f"{today},{dataset_downloads}\n")

def load_log(filepath):
    if not os.path.exists(filepath):
        return [], []

    unique_records = []
    seen_records = set()
    with open(filepath, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 2:
                continue
            date_str = parts[0].strip()
            try:
                value = int(parts[1].strip())
            except ValueError:
                continue

            record_key = (date_str, value)
            if record_key in seen_records:
                continue
            seen_records.add(record_key)
            unique_records.append(record_key)

    dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d") for d in unique_records]
    values = [d[1] for d in unique_records]
    return dates, values

def draw_plot():
    dates_model, values_model = load_log(MODEL_LOG_FILE)
    dates_data, values_data = load_log(DATASET_LOG_FILE)

    # 计算12个月前的日期
    today = datetime.date.today()
    twelve_months_ago = today - datetime.timedelta(days=365)
    
    # 创建月份字典来存储每月下载量
    monthly_model_downloads = {}
    monthly_dataset_downloads = {}
    
    # 处理模型下载数据
    for date, value in zip(dates_model, values_model):
        if date.date() >= twelve_months_ago:
            month_key = date.strftime("%Y-%m")
            if month_key in monthly_model_downloads:
                monthly_model_downloads[month_key] += value
            else:
                monthly_model_downloads[month_key] = value
    
    # 处理数据集下载数据
    for date, value in zip(dates_data, values_data):
        if date.date() >= twelve_months_ago:
            month_key = date.strftime("%Y-%m")
            if month_key in monthly_dataset_downloads:
                monthly_dataset_downloads[month_key] += value
            else:
                monthly_dataset_downloads[month_key] = value
    
    # 获取所有有记录的月份并排序
    all_months = sorted(list(set(monthly_model_downloads.keys()) | set(monthly_dataset_downloads.keys())))
    
    # 只保留最近12个月的数据
    if len(all_months) > 12:
        all_months = all_months[-12:]
    
    # 获取每月的下载量
    model_monthly_values = [monthly_model_downloads.get(month, 0) for month in all_months]
    dataset_monthly_values = [monthly_dataset_downloads.get(month, 0) for month in all_months]
    
    # 美化月份标签显示
    display_months = [f"{month[-2:]}/{month[:4]}" for month in all_months]
    x = range(len(display_months))

    publication_style = {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "STIXGeneral"],
        "mathtext.fontset": "stix",
        "axes.linewidth": 0.8,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 300,
        "savefig.dpi": 300,
    }

    total_model_downloads = sum(values_model)
    total_dataset_downloads = sum(values_data)

    with plt.rc_context(publication_style):
        fig, (ax_monthly, ax_total) = plt.subplots(
            1,
            2,
            figsize=(10.2, 4.5),
            gridspec_kw={"width_ratios": [2.3, 1.0]},
        )
        fig.patch.set_facecolor("white")
        ax_monthly.set_facecolor("white")
        ax_total.set_facecolor("white")

        # 色盲友好配色，论文中可读性更强
        model_color = "#1B6CA8"
        dataset_color = "#D95F02"

        # 左图：按月份统计（最近12个月）
        ax_monthly.plot(
            x,
            model_monthly_values,
            label="Model downloads",
            color=model_color,
            linewidth=1.8,
            linestyle="-",
            marker="o",
            markersize=4.5,
            markerfacecolor="white",
            markeredgewidth=1.1,
            zorder=3,
        )
        ax_monthly.plot(
            x,
            dataset_monthly_values,
            label="Dataset downloads",
            color=dataset_color,
            linewidth=1.8,
            linestyle="--",
            marker="s",
            markersize=4.3,
            markerfacecolor="white",
            markeredgewidth=1.1,
            zorder=3,
        )

        ax_monthly.set_xticks(list(x))
        ax_monthly.set_xticklabels(display_months, rotation=30, ha="right")
        ax_monthly.set_ylabel("Monthly downloads")
        ax_monthly.set_xlabel("Month")
        ax_monthly.set_title("Monthly Downloads (Last 12 Months)", pad=8)
        ax_monthly.yaxis.set_major_formatter(FuncFormatter(_format_thousands))
        ax_monthly.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax_monthly.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.45, color="#9A9A9A")
        ax_monthly.grid(axis="x", visible=False)
        ax_monthly.legend(loc="upper left", frameon=False)

        # 右图：总下载量（基于全部去重记录）
        categories = ["Model", "Dataset"]
        totals = [total_model_downloads, total_dataset_downloads]
        bars = ax_total.bar(
            categories,
            totals,
            color=[model_color, dataset_color],
            width=0.62,
            edgecolor="#333333",
            linewidth=0.6,
            zorder=3,
        )
        ax_total.set_title("Total Downloads", pad=8)
        ax_total.set_ylabel("Downloads")
        ax_total.yaxis.set_major_formatter(FuncFormatter(_format_thousands))
        ax_total.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax_total.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.45, color="#9A9A9A")
        ax_total.grid(axis="x", visible=False)

        y_top = max(totals) if totals else 0
        for bar, value in zip(bars, totals):
            ax_total.text(
                bar.get_x() + bar.get_width() / 2,
                value + max(y_top * 0.015, 1),
                f"{value:,}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                color="#333333",
            )
        ax_total.set_ylim(0, y_top * 1.12 if y_top > 0 else 1)

        for axis in (ax_monthly, ax_total):
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
            axis.spines["left"].set_color("#4D4D4D")
            axis.spines["bottom"].set_color("#4D4D4D")
            axis.tick_params(axis="both", direction="out", length=3.5, width=0.8, color="#4D4D4D")

        fig.tight_layout()
        fig.savefig(PLOT_FILE, bbox_inches="tight", facecolor="white")
        plt.close(fig)

def get_downloads():
    _, model_values = load_log(MODEL_LOG_FILE)
    _, dataset_values = load_log(DATASET_LOG_FILE)
    total_model_downloads = sum(model_values)
    total_dataset_downloads = sum(dataset_values)
    
    # 加上千分位
    total_model_downloads = "{:,}".format(total_model_downloads)
    total_dataset_downloads = "{:,}".format(total_dataset_downloads)
    
    return total_model_downloads, total_dataset_downloads


if __name__ == "__main__":
    model_dl, dataset_dl = get_hf_downloads(HF_USERNAME)
    log_downloads(model_dl, dataset_dl)
    model_downloads, dataset_downloads = get_downloads()
    print(f"model_downloads: {model_downloads}, dataset_downloads: {dataset_downloads}")
    draw_plot()
    print("✅ 下载量已记录并生成美化图表。")
