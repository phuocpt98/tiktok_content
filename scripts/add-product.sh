#!/bin/bash
# Tạo folder sản phẩm mới từ template
# Usage: bash scripts/add-product.sh ten-san-pham "Tên Sản Phẩm"

PRODUCT_DIR="assets/products"
TEMPLATE_DIR="$PRODUCT_DIR/_template"

if [ -z "$1" ]; then
  echo "Usage: bash scripts/add-product.sh <slug> <ten-san-pham>"
  echo "Example: bash scripts/add-product.sh mi-cay-samyang \"Mì Cay Samyang\""
  exit 1
fi

SLUG="$1"
NAME="${2:-$1}"
TARGET="$PRODUCT_DIR/$SLUG"

if [ -d "$TARGET" ]; then
  echo "Product '$SLUG' already exists!"
  exit 1
fi

mkdir -p "$TARGET"/{photos,videos,info}
sed "s/\[Tên sản phẩm\]/$NAME/" "$TEMPLATE_DIR/info/product.md" > "$TARGET/info/product.md"
echo "Created: $TARGET/"
echo "  photos/  — push ảnh vào đây"
echo "  videos/  — push video vào đây"
echo "  info/product.md — điền thông tin sản phẩm"
