#!/usr/bin/env bash
# GEO.DB Complete Setup Script
# شاخص کامل نصب و راه‌اندازی سیستم GEO.DB

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║         🗄️  GEO.DB - سیستم پایگاه داده جغرافیایی            ║"
    echo "║                                                                ║"
    echo "║    سیستم مدیریت و جستجوی داده‌های جغرافیایی بندرعباس        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print step header
print_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ مرحله: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Print info
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python
check_python() {
    print_step "بررسی Python"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 یافت نشد"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION یافت شد"
}

# Check dependencies
check_dependencies() {
    print_step "بررسی فایل‌های مورد نیاز"
    
    local required_files=(
        "database/schema.sql"
        "database/schema_admin_geo.sql"
        "hormozgan_atlas_dictionary.json"
        "bandar_places.json"
        "init_geodb.py"
        "import_hormozgan_atlas.py"
        "import_bandar_places.py"
        "generate_places_kb.py"
    )
    
    local missing=0
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✓ $file"
        else
            print_error "یافت نشد: $file"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        print_error "$missing فایل یافت نشد"
        exit 1
    fi
    
    print_success "تمام فایل‌های مورد نیاز موجود هستند"
}

# Initialize database
init_database() {
    print_step "مقداردهی اولیه پایگاه داده"
    
    if [ -f "geo.db" ]; then
        print_info "پایگاه داده قبلاً موجود است"
        print_info "نسخه پشتیبانی ایجاد می‌شود..."
        mv geo.db "geo.db.backup.$(date +%s)"
        print_success "نسخه پشتیبانی ایجاد شد"
    fi
    
    python3 init_geodb.py --db geo.db
    print_success "پایگاه داده راه‌اندازی شد"
}

# Import atlas data
import_atlas() {
    print_step "وارد کردن داده‌های جغرافیایی هرمزگان"
    
    python3 import_hormozgan_atlas.py \
        --db geo.db \
        --atlas hormozgan_atlas_dictionary.json
    
    print_success "داده‌های هرمزگان وارد شدند"
}

# Import places
import_places() {
    print_step "وارد کردن 677 مکان بندرعباس"
    
    python3 import_bandar_places.py \
        --db geo.db \
        --places bandar_places.json
    
    print_success "مکان‌ها وارد شدند"
}

# Generate knowledge base
generate_kb() {
    print_step "ایجاد دانشنامه و شاخص جستجو"
    
    python3 generate_places_kb.py --db geo.db
    
    print_success "دانشنامه و شاخص ایجاد شدند"
}

# Verify installation
verify_installation() {
    print_step "تأیید نصب"
    
    echo ""
    echo "  📊 آمار پایگاه داده:"
    echo ""
    
    sqlite3 geo.db <<EOF
    .headers on
    .mode column
    SELECT 'Geo Counties' as [Type], COUNT(*) as [Count] FROM geo_counties
    UNION ALL
    SELECT 'Geo Islands', COUNT(*) FROM geo_islands
    UNION ALL
    SELECT 'Places', COUNT(*) FROM places
    UNION ALL
    SELECT 'POIs', COUNT(*) FROM pois;
EOF
    
    echo ""
    echo "  📁 فایل‌های تولید شده:"
    echo ""
    
    if [ -f "geo.db" ]; then
        size=$(du -h geo.db | cut -f1)
        echo "    ✓ geo.db ($size)"
    fi
    
    if [ -f "bandar_places_knowledge.json" ]; then
        size=$(du -h bandar_places_knowledge.json | cut -f1)
        echo "    ✓ bandar_places_knowledge.json ($size)"
    fi
    
    if [ -f "bandar_places_search_index.json" ]; then
        size=$(du -h bandar_places_search_index.json | cut -f1)
        echo "    ✓ bandar_places_search_index.json ($size)"
    fi
    
    print_success "نصب تأیید شد"
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                     ✅ نصب موفقیت‌آمیز بود                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    echo ""
    echo -e "${YELLOW}📚 مراحل بعدی:${NC}"
    echo ""
    echo -e "${BLUE}1. مستندات را مطالعه کنید:${NC}"
    echo "   • docs/GEO_DB_GUIDE.md - راهنمای جامع"
    echo "   • docs/QUICK_START.md - راهنمای سریع"
    echo "   • README_GEO_DB.md - معرفی سیستم"
    echo ""
    
    echo -e "${BLUE}2. از Python API استفاده کنید:${NC}"
    echo "   from geodb import Places, Counties, Islands"
    echo "   with Places() as places:"
    echo "       results = places.search_by_name('کافه')"
    echo ""
    
    echo -e "${BLUE}3. پایگاه داده را پرس‌وجو کنید:${NC}"
    echo "   sqlite3 geo.db"
    echo "   SELECT * FROM places WHERE category = 'restaurant';"
    echo ""
    
    echo -e "${BLUE}4. نمونه‌های پیشرفته:${NC}"
    echo "   python3 -c 'from geodb import Places; Places().connect(); ...'"
    echo ""
    
    echo -e "${GREEN}مبارک است! سیستم GEO.DB آماده به کار است! 🎉${NC}"
    echo ""
}

# Main execution
main() {
    print_banner
    
    print_info "شروع نصب و راه‌اندازی GEO.DB"
    print_info "زمان تخمینی: 2-3 دقیقه"
    echo ""
    
    # Check for Python 3.7+
    check_python
    
    # Check dependencies
    check_dependencies
    
    # Initialize
    init_database
    
    # Import data
    import_atlas
    import_places
    
    # Generate KB
    generate_kb
    
    # Verify
    verify_installation
    
    # Print next steps
    print_next_steps
}

# Error handling
trap 'print_error "خرابی در نصب رخ داد"; exit 1' ERR

# Run main
main
