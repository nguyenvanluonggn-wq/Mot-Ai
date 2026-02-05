#!/usr/bin/env python3
# Build script để tạo executable

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_app():
    """Build ứng dụng thành executable"""
    
    print("=" * 60)
    print("Building AI Story Creator Pro...")
    print("=" * 60)
    
    # Đường dẫn
    current_dir = Path(__file__).parent
    src_dir = current_dir / 'src'
    assets_dir = current_dir / 'assets'
    build_dir = current_dir / 'build'
    dist_dir = current_dir / 'dist'
    
    # Kiểm tra file main.py
    main_py = src_dir / 'main.py'
    if not main_py.exists():
        print(f"❌ Lỗi: Không tìm thấy {main_py}")
        return
    
    print(f"✅ Tìm thấy main.py tại: {main_py}")
    
    # Tạo thư mục build nếu chưa có
    build_dir.mkdir(exist_ok=True)
    
    # Copy assets
    print("\n📁 Copying assets...")
    if assets_dir.exists():
        dest_assets = build_dir / 'assets'
        if dest_assets.exists():
            shutil.rmtree(dest_assets)
        shutil.copytree(assets_dir, dest_assets)
    
    # PyInstaller arguments - XÂY DỰNG TỪ src/main.py
    pyinstaller_args = [
        str(main_py),  # Đường dẫn đầy đủ đến main.py
        '--name=AI_Story_Creator_Pro',
        '--windowed',  # Không hiển thị console
        f'--icon={assets_dir / "icon.ico"}',
        f'--add-data={assets_dir}{os.pathsep}assets',
        f'--add-data={current_dir / "config.json"}{os.pathsep}.',
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._imagingtk',
        '--hidden-import=PIL._tkinter_finder',
        '--collect-all=customtkinter',
        '--collect-all=PIL',
        '--clean',
        '--noconfirm',
        f'--paths={src_dir}',  # Thêm src vào PYTHONPATH
    ]
    
    # Build
    print("\n🚀 Building executable...")
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("\n✅ Build completed!")
    print(f"📁 Output: {dist_dir / 'AI_Story_Creator_Pro'}")
    
    # Copy additional files
    print("\n📋 Copying additional files...")
    
    files_to_copy = ['config.json', 'README.md']
    
    for file_name in files_to_copy:
        src_file = current_dir / file_name
        if src_file.exists():
            dest_file = dist_dir / 'AI_Story_Creator_Pro' / file_name
            shutil.copy2(src_file, dest_file)
    
    print("\n🎉 Build process completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run the executable from dist/AI_Story_Creator_Pro/")
    print("2. Make sure LM Studio is running on http://localhost:1234")
    print("3. For image generation, run Stable Diffusion WebUI")
    print("\nNeed help? Check README.md for more information.")

if __name__ == "__main__":
    build_app()
