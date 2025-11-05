#!/usr/bin/env python3
"""
FineWeb-Data 数据集读取示例

此脚本展示多种读取HuggingFace数据集的方法
适用于 FineWeb-Data 处理的数据集

使用方法:
python read_dataset_examples.py --dataset pohsjxx/fineweb-data-data-law
"""

import argparse
import os
from dotenv import load_dotenv
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download
import pandas as pd


def load_environment():
    """加载环境变量"""
    # 尝试多个位置的.env文件
    for env_path in ['.env', '../.env', './.env']:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ 加载环境变量: {env_path}")
            return True
    print("⚠️  未找到.env文件")
    return False


def method_1_datasets_library(dataset_id, token):
    """方法1: 使用datasets库 (推荐)"""
    print("\n" + "="*50)
    print("方法1: 使用datasets库 (推荐)")
    print("="*50)

    # 加载数据集
    ds = load_dataset(dataset_id, token=token)
    print(f"数据集结构: {ds}")

    # 访问训练集
    train_data = ds['train']
    print(f"训练集大小: {len(train_data)} 个样本")
    print(f"列名: {train_data.column_names}")

    # 查看第一个样本
    if len(train_data) > 0:
        sample = train_data[0]
        print("\n第一个样本:")
        for key, value in sample.items():
            if key == 'text' and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")

    return ds


def method_2_pandas_analysis(dataset_id, token):
    """方法2: 使用pandas进行数据分析"""
    print("\n" + "="*50)
    print("方法2: pandas数据分析")
    print("="*50)

    # 加载并转换为DataFrame
    ds = load_dataset(dataset_id, token=token)
    df = ds['train'].to_pandas()

    print("DataFrame信息:")
    print(df.info())

    # 展开metadata列
    if 'metadata' in df.columns:
        metadata_df = pd.json_normalize(df['metadata'])
        full_df = pd.concat([df.drop('metadata', axis=1), metadata_df], axis=1)
        print(f"\n展开后的DataFrame形状: {full_df.shape}")
        print(f"所有列: {list(full_df.columns)}")

    # 基本统计
    if len(df) > 0:
        print("
统计信息:")
        if 'text' in df.columns:
            print(f"  文本平均长度: {df['text'].str.len().mean():.0f} 字符")
            print(f"  文本最大长度: {df['text'].str.len().max()} 字符")

        # 检查metadata统计
        if 'metadata' in df.columns and len(df['metadata']) > 0:
            sample_meta = df['metadata'].iloc[0]
            if isinstance(sample_meta, dict):
                if 'token_count' in sample_meta:
                    token_counts = [m.get('token_count', 0) for m in df['metadata'] if isinstance(m, dict)]
                    print(f"  Token数平均值: {sum(token_counts)/len(token_counts):.0f}")
                if 'language_score' in sample_meta:
                    lang_scores = [m.get('language_score', 0) for m in df['metadata'] if isinstance(m, dict)]
                    print(f"  语言置信度: {sum(lang_scores)/len(lang_scores):.3f}")

    return df


def method_3_direct_download(dataset_id, token):
    """方法3: 直接下载Parquet文件"""
    print("\n" + "="*50)
    print("方法3: 直接下载Parquet文件")
    print("="*50)

    try:
        # 下载Parquet文件
        file_path = hf_hub_download(
            repo_id=dataset_id,
            filename='data/train-00000-of-00001.parquet',
            repo_type='dataset',
            token=token
        )

        print(f"文件下载到: {file_path}")
        print(f"文件大小: {os.path.getsize(file_path)} bytes")

        # 读取Parquet文件
        df = pd.read_parquet(file_path)
        print(f"数据形状: {df.shape}")
        print(f"列: {list(df.columns)}")

        return df

    except Exception as e:
        print(f"下载失败: {e}")
        return None


def method_4_streaming_large_dataset(dataset_id, token):
    """方法4: 流式处理大数据集"""
    print("\n" + "="*50)
    print("方法4: 流式处理 (适用于大文件)")
    print("="*50)

    # 流式加载
    ds = load_dataset(dataset_id, token=token, streaming=True)
    train_stream = ds['train']

    print("流式处理示例:")
    count = 0
    total_tokens = 0

    for sample in train_stream:
        count += 1
        text_len = len(sample['text'])
        tokens = sample.get('metadata', {}).get('token_count', 0)
        total_tokens += tokens

        print(f"样本 {count}: {text_len} 字符, {tokens} tokens")
        print(f"  预览: {sample['text'][:50]}...")

        if count >= 5:  # 只处理前5个样本作为示例
            break

    print(f"\n总共处理了 {count} 个样本")
    if count > 0:
        print(f"平均token数: {total_tokens/count:.0f}")


def method_5_dataset_filtering(dataset_id, token):
    """方法5: 数据过滤和查询"""
    print("\n" + "="*50)
    print("方法5: 数据过滤和查询")
    print("="*50)

    ds = load_dataset(dataset_id, token=token)
    train_data = ds['train']

    # 各种过滤示例
    filters = {
        "长文本 (>1000字符)": lambda x: len(x['text']) > 1000,
        "包含'law'关键词": lambda x: 'law' in x['text'].lower(),
        "高质量语言检测": lambda x: x.get('metadata', {}).get('language_score', 0) > 0.8,
        "数据法律相关": lambda x: any(term in x['text'].lower() for term in ['legal', 'compliance', 'regulation', 'privacy'])
    }

    for filter_name, filter_func in filters.items():
        filtered = [sample for sample in train_data if filter_func(sample)]
        print(f"{filter_name}: {len(filtered)} 个样本")


def main():
    parser = argparse.ArgumentParser(description='FineWeb-Data 数据集读取示例')
    parser.add_argument('--dataset', default='pohsjxx/fineweb-data-data-law',
                       help='数据集ID (默认: pohsjxx/fineweb-data-data-law)')
    parser.add_argument('--method', choices=['1', '2', '3', '4', '5', 'all'],
                       default='all', help='选择读取方法 (默认: all)')

    args = parser.parse_args()

    # 加载环境变量
    if not load_environment():
        print("请确保设置了HF_TOKEN环境变量")
        return

    token = os.getenv('HF_TOKEN')
    if not token:
        print("❌ 未找到HF_TOKEN环境变量")
        return

    print(f"🎯 目标数据集: {args.dataset}")

    try:
        if args.method in ['1', 'all']:
            ds = method_1_datasets_library(args.dataset, token)

        if args.method in ['2', 'all']:
            df = method_2_pandas_analysis(args.dataset, token)

        if args.method in ['3', 'all']:
            df_downloaded = method_3_direct_download(args.dataset, token)

        if args.method in ['4', 'all']:
            method_4_streaming_large_dataset(args.dataset, token)

        if args.method in ['5', 'all']:
            method_5_dataset_filtering(args.dataset, token)

        print("\n" + "="*50)
        print("✅ 数据集读取完成!")
        print("="*50)

    except Exception as e:
        print(f"❌ 读取失败: {e}")


if __name__ == '__main__':
    main()
