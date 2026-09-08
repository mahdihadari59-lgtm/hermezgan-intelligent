import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

const DashboardScreen = () => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📊 داشبورد تحلیلی</Text>
        <Text style={styles.headerSubtitle}>نمای کلی عملکرد سیستم</Text>
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statIcon}>👥</Text>
          <Text style={styles.statValue}>۱,۲۳۴</Text>
          <Text style={styles.statLabel}>کاربران کل</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statIcon}>🟢</Text>
          <Text style={styles.statValue}>۸۵۶</Text>
          <Text style={styles.statLabel}>کاربران فعال</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statIcon}>🏪</Text>
          <Text style={styles.statValue}>۵۶۷</Text>
          <Text style={styles.statLabel}>خدمات</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statIcon}>💬</Text>
          <Text style={styles.statValue}>۳,۴۲۱</Text>
          <Text style={styles.statLabel}>چت‌ها</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📈 فعالیت‌های اخیر</Text>
        <View style={styles.activityItem}>
          <Text style={styles.activityUser}>علی محمدی</Text>
          <Text style={styles.activityAction}>جستجوی بیمارستان</Text>
          <Text style={styles.activityTime}>۱۰ دقیقه پیش</Text>
        </View>
        <View style={styles.activityItem}>
          <Text style={styles.activityUser}>فاطمه احمدی</Text>
          <Text style={styles.activityAction}>درخواست مسیریابی</Text>
          <Text style={styles.activityTime}>۲۵ دقیقه پیش</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  header: { backgroundColor: '#667eea', padding: 24, alignItems: 'center' },
  headerTitle: { fontSize: 22, fontWeight: 'bold', color: 'white' },
  headerSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.8)', marginTop: 4 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', padding: 12, gap: 12 },
  statCard: { flex: 1, minWidth: '45%', backgroundColor: 'white', padding: 16, borderRadius: 12, alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
  statIcon: { fontSize: 28 },
  statValue: { fontSize: 20, fontWeight: 'bold', color: '#2d3748', marginTop: 4 },
  statLabel: { fontSize: 12, color: '#a0aec0', marginTop: 2 },
  section: { backgroundColor: 'white', margin: 12, padding: 16, borderRadius: 12 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#2d3748', marginBottom: 12 },
  activityItem: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f0f2f5' },
  activityUser: { fontSize: 14, fontWeight: '600', color: '#2d3748' },
  activityAction: { fontSize: 14, color: '#718096' },
  activityTime: { fontSize: 12, color: '#a0aec0' },
});

export default DashboardScreen;
