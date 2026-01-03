#!/usr/bin/env python3
"""
Usage:
    python translator.py --input xxxx.md --prompt prompt.md

環境変数 OPENAI_API_KEY に OpenAI API キーを設定しておく必要があります。
"""

import argparse
import os
import sys

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI()

def request_to_model(model_name, prompt, timeout=130):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'user', 'content': prompt},
            ],
            timeout=timeout
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR in {model_name}]: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description='Markdown下書きをOpenAI APIで英訳し、`_EN.md`ファイルを出力します。'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='入力下書きMarkdownファイルのパス (例: draft.md)'
    )
    parser.add_argument(
        '--prompt', '-p',
        required=True,
        help='プロンプトテンプレートファイルのパス (例: prompt.md)'
    )
    args = parser.parse_args()

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('Error: 環境変数 OPENAI_API_KEY を設定してください。', file=sys.stderr)
        sys.exit(1)
    openai.api_key = api_key

    # プロンプトテンプレートを読み込み
    try:
        with open(args.prompt, 'r', encoding='utf-8') as pf:
            prompt_template = pf.read()
    except Exception as e:
        print(f'Error: プロンプトファイルの読み込みに失敗しました: {e}', file=sys.stderr)
        sys.exit(1)

    # 下書き本文を読み込み
    try:
        with open(args.input, 'r', encoding='utf-8') as inf:
            body = inf.read()
    except Exception as e:
        print(f'Error: 入力ファイルの読み込みに失敗しました: {e}', file=sys.stderr)
        sys.exit(1)

    # %body% を置換してオフィシャルプロンプトを生成
    official_prompt = prompt_template.replace('%body%', body)

    # OpenAI API で英訳を取得
    translation = request_to_model('gpt-5.2', official_prompt)

    # 後処理
    translation = translation.replace("’", "'") # プロンプトでも直らんので荒療治

    # 出力ファイル名を生成して書き込み
    base, ext = os.path.splitext(args.input)
    output_file = f"{base}_EN{ext}"
    try:
        with open(output_file, 'w', encoding='utf-8') as outf:
            outf.write(translation)
    except Exception as e:
        print(f'Error: 出力ファイルの書き込みに失敗しました: {e}', file=sys.stderr)
        sys.exit(1)

    print(f'Translatorが正常に完了しました。生成ファイル: {output_file}')

if __name__ == '__main__':
    main()
