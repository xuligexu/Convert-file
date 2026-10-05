"""
命令行接口
"""
import argparse
import sys
from converter import PDFTXTConverter


def main():
    parser = argparse.ArgumentParser(
        description="PDF ↔ TXT 文件互转工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python cli.py pdf2txt input.pdf output.txt
  python cli.py txt2pdf input.txt output.pdf
  python cli.py pdf2txt input_dir/ output_dir/ --batch
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # pdf2txt 子命令
    pdf2txt_parser = subparsers.add_parser("pdf2txt", help="PDF 转 TXT")
    pdf2txt_parser.add_argument("input", help="输入 PDF 文件或目录")
    pdf2txt_parser.add_argument("output", help="输出 TXT 文件或目录")
    pdf2txt_parser.add_argument("--batch", action="store_true", help="批量转换模式")

    # txt2pdf 子命令
    txt2pdf_parser = subparsers.add_parser("txt2pdf", help="TXT 转 PDF")
    txt2pdf_parser.add_argument("input", help="输入 TXT 文件或目录")
    txt2pdf_parser.add_argument("output", help="输出 PDF 文件或目录")
    txt2pdf_parser.add_argument("--batch", action="store_true", help="批量转换模式")
    txt2pdf_parser.add_argument("--font-size", type=int, default=12, help="字号（默认 12）")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    converter = PDFTXTConverter()

    if args.batch:
        direction = args.command
        print(f"📂 批量转换模式：{direction}")
        stats = converter.batch_convert(args.input, args.output, direction)
        print(f"\n✅ 成功: {stats['success']}")
        print(f"❌ 失败: {stats['failed']}")
        if stats["files"]:
            print("\n生成的文件:")
            for f in stats["files"]:
                print(f"  - {f}")
    else:
        if args.command == "pdf2txt":
            print(f"📄 正在将 {args.input} 转换为 TXT...")
            if converter.pdf_to_txt(args.input, args.output):
                print(f"✅ 转换成功: {args.output}")
            else:
                sys.exit(1)
        else:  # txt2pdf
            print(f"📝 正在将 {args.input} 转换为 PDF...")
            if converter.txt_to_pdf(args.input, args.output,
                                    font_size=args.font_size):
                print(f"✅ 转换成功: {args.output}")
            else:
                sys.exit(1)


if __name__ == "__main__":
    main()