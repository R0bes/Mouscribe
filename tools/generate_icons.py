#!/usr/bin/env python3
"""
Icon Generator for Mauscribe
Converts SVG icons to ICO/PNG formats with multiple sizes.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import cairosvg
    from PIL import Image
except ImportError:
    print("❌ Missing dependencies. Install with: pip install pillow cairosvg")
    sys.exit(1)


class IconGenerator:
    """Generates icons in various formats and sizes."""

    def __init__(self, source_dir: str = "src/ui/icons", output_dir: str = "src/ui/icons"):
        """Initialize icon generator."""
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.sizes = [16, 32, 64, 128, 256]

    def svg_to_png(self, svg_path: Path, png_path: Path, size: int) -> None:
        """Convert SVG to PNG with specified size."""
        try:
            # Convert SVG to PNG using cairosvg
            png_data = cairosvg.svg2png(url=str(svg_path), output_width=size, output_height=size)

            # Save PNG
            with open(png_path, "wb") as f:
                f.write(png_data)

            print(f"[OK] Generated: {png_path.name} ({size}x{size})")

        except Exception as e:
            print(f"[ERROR] Failed to convert {svg_path.name}: {e}")

    def png_to_ico(self, png_paths: list[Path], ico_path: Path) -> None:
        """Convert multiple PNG files to ICO."""
        try:
            images = []
            for png_path in png_paths:
                if png_path.exists():
                    img = Image.open(png_path)
                    images.append(img)

            if images:
                images[0].save(ico_path, format="ICO", sizes=[(img.width, img.height) for img in images])
                print(f"[OK] Generated: {ico_path.name}")
            else:
                print(f"[ERROR] No PNG files found for {ico_path.name}")

        except Exception as e:
            print(f"[ERROR] Failed to create ICO {ico_path.name}: {e}")

    def generate_icon_set(self, svg_name: str) -> None:
        """Generate complete icon set from SVG."""
        svg_path = self.source_dir / f"{svg_name}.svg"

        if not svg_path.exists():
            print(f"[WARN] SVG not found: {svg_path}")
            return

        # Generate PNG files for different sizes
        png_paths = []
        for size in self.sizes:
            png_path = self.output_dir / f"{svg_name}_{size}.png"
            self.svg_to_png(svg_path, png_path, size)
            png_paths.append(png_path)

        # Generate ICO file
        ico_path = self.output_dir / f"{svg_name}.ico"
        self.png_to_ico(png_paths, ico_path)

        # Generate main PNG (256x256)
        main_png = self.output_dir / f"{svg_name}.png"
        if png_paths:
            main_img = Image.open(png_paths[-1])  # Use largest size
            main_img.save(main_png)
            print(f"[OK] Generated: {main_png.name}")

    def generate_ui_icons(self) -> None:
        """Generate UI icons from SVG sources."""
        ui_dir = self.source_dir / "ui"

        if not ui_dir.exists():
            print(f"[WARN] UI icons directory not found: {ui_dir}")
            return

        svg_files = list(ui_dir.glob("*.svg"))

        if not svg_files:
            print("[WARN] No SVG files found in UI directory")
            return

        print(f"[INFO] Generating {len(svg_files)} UI icons...")

        for svg_file in svg_files:
            icon_name = svg_file.stem

            # Generate PNG files for different sizes
            for size in [16, 24, 32]:
                png_path = ui_dir / f"{icon_name}_{size}.png"
                self.svg_to_png(svg_file, png_path, size)

            print(f"[OK] Generated UI icon set: {icon_name}")

    def generate_all_icons(self) -> None:
        """Generate all icon sets."""
        print("Mauscribe Icon Generator")
        print("=" * 40)

        # Main icons
        main_icons = ["icon_idle", "icon_record", "icon"]

        for icon_name in main_icons:
            print(f"\n[INFO] Generating {icon_name}...")
            self.generate_icon_set(icon_name)

        # UI icons
        print("\n[INFO] Generating UI icons...")
        self.generate_ui_icons()

        print("\n[SUCCESS] Icon generation complete!")
        self._print_summary()

    def _print_summary(self) -> None:
        """Print summary of generated files."""
        print("\nGenerated Files:")
        print("-" * 30)

        # Count files by type
        png_count = len(list(self.output_dir.rglob("*.png")))
        ico_count = len(list(self.output_dir.rglob("*.ico")))
        svg_count = len(list(self.output_dir.rglob("*.svg")))

        print(f"SVG sources: {svg_count}")
        print(f"PNG files: {png_count}")
        print(f"ICO files: {ico_count}")

        print(f"\nOutput directory: {self.output_dir.absolute()}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mauscribe Icon Generator")
    parser.add_argument("--source", default="src/ui/icons", help="Source directory")
    parser.add_argument("--output", default="src/ui/icons", help="Output directory")
    parser.add_argument("--icon", help="Generate specific icon only")
    parser.add_argument("--ui-only", action="store_true", help="Generate UI icons only")

    args = parser.parse_args()

    generator = IconGenerator(args.source, args.output)

    try:
        if args.icon:
            generator.generate_icon_set(args.icon)
        elif args.ui_only:
            generator.generate_ui_icons()
        else:
            generator.generate_all_icons()
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
