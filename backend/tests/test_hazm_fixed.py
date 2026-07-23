#!/usr/bin/env python
# ============================================================
# تست Hazm - نسخه سازگار با Python 3.14
# ============================================================

import sys
import re
import warnings

# نادیده گرفتن هشدارها
warnings.filterwarnings('ignore')

def test_import_hazm():
    """تست import Hazm"""
    try:
        import hazm
        print("✅ Hazm version:", hazm.__version__)
        return True
    except ImportError as e:
        print(f"❌ Hazm import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Hazm error: {e}")
        return False

def test_simple_tokenization():
    """تست توکن‌سازی ساده"""
    try:
        # توکن‌سازی دستی
        text = "سلام! من هرمزگان هوشمند هستم."
        # حذف علائم
        cleaned = re.sub(r'[،؛؟!\.\-\"\']', ' ', text)
        tokens = cleaned.split()
        print("🔤 توکن‌ها:", tokens)
        print(f"📊 تعداد: {len(tokens)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_hazm_basic():
    """تست عملکرد پایه Hazm"""
    try:
        from hazm import Normalizer
        
        normalizer = Normalizer()
        text = "سلام! من هرمزگان هوشمند هستم."
        result = normalizer.normalize(text)
        print("📝 نرمال‌سازی:", result)
        return True
    except Exception as e:
        print(f"⚠️ Hazm basic error: {e}")
        return False

def test_hazm_tokenizer():
    """تست توکن‌ساز Hazm"""
    try:
        from hazm import word_tokenize
        from hazm import Normalizer
        
        normalizer = Normalizer()
        text = normalizer.normalize("سلام! من هرمزگان هوشمند هستم.")
        tokens = word_tokenize(text)
        print("🔤 توکن‌های Hazm:", tokens)
        return True
    except Exception as e:
        print(f"⚠️ Hazm tokenizer error: {e}")
        return False

def test_hazm_lemmatizer():
    """تست Lemmatizer Hazm"""
    try:
        from hazm import Lemmatizer
        
        lemmatizer = Lemmatizer()
        words = ["می‌روم", "رفتم", "می‌رویم"]
        print("📖 Lemmatization:")
        for word in words:
            result = lemmatizer.lemmatize(word)
            print(f"  {word} → {result}")
        return True
    except Exception as e:
        print(f"⚠️ Hazm lemmatizer error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 تست Hazm - Python 3.14 Compatible")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Hazm", test_import_hazm),
        ("Simple Tokenization", test_simple_tokenization),
        ("Hazm Normalizer", test_hazm_basic),
        ("Hazm Tokenizer", test_hazm_tokenizer),
        ("Hazm Lemmatizer", test_hazm_lemmatizer),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n▶️ {name}:")
        print("-" * 40)
        try:
            result = test_func()
            if result:
                passed += 1
                print("✅ موفق")
            else:
                failed += 1
                print("❌ ناموفق")
        except Exception as e:
            failed += 1
            print(f"❌ خطا: {e}")
    
    print()
    print("=" * 60)
    print(f"📊 خلاصه: ✅ {passed} موفق, ❌ {failed} ناموفق")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
