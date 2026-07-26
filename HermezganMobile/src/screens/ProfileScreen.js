import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';

const ProfileScreen = () => {
  return (
    <View style={styles.container}>
      <View style={styles.profileHeader}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatarText}>👤</Text>
        </View>
        <Text style={styles.profileName}>کاربر مهمان</Text>
        <Text style={styles.profileEmail}>guest@hermezgan.ir</Text>
      </View>

      <View style={styles.menuSection}>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuIcon}>📋</Text>
          <Text style={styles.menuText}>اطلاعات شخصی</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuIcon}>⚙️</Text>
          <Text style={styles.menuText}>تنظیمات</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuIcon}>🔐</Text>
          <Text style={styles.menuText}>تغییر رمز عبور</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuIcon}>📊</Text>
          <Text style={styles.menuText}>آمار کاربری</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.menuItem, styles.logoutItem]}>
          <Text style={styles.menuIcon}>🚪</Text>
          <Text style={[styles.menuText, styles.logoutText]}>خروج</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>نسخه ۱.۰.۰</Text>
        <Text style={styles.footerText}>🌊 هرمزگان هوشمند</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  profileHeader: { backgroundColor: '#667eea', padding: 32, alignItems: 'center' },
  avatarContainer: { width: 80, height: 80, borderRadius: 40, backgroundColor: 'white', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 40 },
  profileName: { fontSize: 20, fontWeight: 'bold', color: 'white', marginTop: 12 },
  profileEmail: { fontSize: 14, color: 'rgba(255,255,255,0.8)', marginTop: 4 },
  menuSection: { backgroundColor: 'white', margin: 16, borderRadius: 12, padding: 8 },
  menuItem: { flexDirection: 'row-reverse', alignItems: 'center', padding: 14, borderBottomWidth: 1, borderBottomColor: '#f0f2f5' },
  menuIcon: { fontSize: 20, marginRight: 12 },
  menuText: { fontSize: 16, color: '#2d3748', flex: 1, textAlign: 'right' },
  logoutItem: { borderBottomWidth: 0 },
  logoutText: { color: '#ff4757' },
  footer: { alignItems: 'center', padding: 20, marginTop: 'auto' },
  footerText: { fontSize: 12, color: '#a0aec0' },
});

export default ProfileScreen;
