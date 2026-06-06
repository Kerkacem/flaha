import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { StatCard } from '../components/StatCard';

export default function ProfileScreen({ navigation }: any) {
  const { farmer, logout, refreshProfile } = useAuth();

  const handleLogout = () => {
    Alert.alert('تسجيل الخروج', 'هل أنت متأكد؟', [
      { text: 'إلغاء', style: 'cancel' },
      { text: 'تسجيل الخروج', style: 'destructive', onPress: logout },
    ]);
  };

  if (!farmer) {
    return (
      <View style={styles.centered}>
        <Text style={styles.notLoggedIn}>غير مسجل الدخول</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.profileHeader}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{farmer.name.charAt(0)}</Text>
        </View>
        <Text style={styles.name}>{farmer.name}</Text>
        <Text style={styles.phone}>{farmer.phone}</Text>
        {farmer.is_verified && <Text style={styles.verifiedBadge}>✓ موثق</Text>}
      </View>

      <View style={styles.statsRow}>
        <StatCard icon="star" label="التقييم" value={farmer.rating_avg?.toFixed(1) || '0.0'} />
        <StatCard icon="swap-horizontal" label="الصفقات" value={farmer.total_transactions || 0} color="#3b82f6" />
        <StatCard icon="checkmark-circle" label="الحالة" value={farmer.is_verified ? 'موثق' : 'غير موثق'} color={farmer.is_verified ? '#16a34a' : '#f59e0b'} />
      </View>

      <View style={styles.infoCard}>
        <Text style={styles.sectionTitle}>المعلومات الشخصية</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>الولاية</Text>
          <Text style={styles.infoValue}>{farmer.wilaya || '--'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>البلدية</Text>
          <Text style={styles.infoValue}>{farmer.commune || '--'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>الدور</Text>
          <Text style={styles.infoValue}>{farmer.role || 'فلاح'}</Text>
        </View>
        {farmer.land_hectares != null && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>مساحة الأرض</Text>
            <Text style={styles.infoValue}>{farmer.land_hectares} هكتار</Text>
          </View>
        )}
        {farmer.credit_score != null && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>الائتمان</Text>
            <Text style={styles.infoValue}>{farmer.credit_score}/100</Text>
          </View>
        )}
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutText}>تسجيل الخروج</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16, paddingBottom: 40 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0fdf4' },
  notLoggedIn: { fontSize: 18, color: '#6b7280', marginBottom: 16 },
  loginBtn: { backgroundColor: '#16a34a', paddingHorizontal: 32, paddingVertical: 12, borderRadius: 10 },
  loginBtnText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  profileHeader: { alignItems: 'center', marginBottom: 20 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#16a34a', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  avatarText: { fontSize: 32, fontWeight: 'bold', color: '#fff' },
  name: { fontSize: 22, fontWeight: 'bold', color: '#1f2937' },
  phone: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  verifiedBadge: { backgroundColor: '#dcfce7', color: '#16a34a', fontWeight: '600', fontSize: 12, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, marginTop: 8 },
  statsRow: { flexDirection: 'row', marginBottom: 16 },
  infoCard: { backgroundColor: '#fff', borderRadius: 16, padding: 20, elevation: 4, marginBottom: 16 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937', marginBottom: 12 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderTopWidth: 1, borderTopColor: '#f3f4f6' },
  infoLabel: { fontSize: 14, color: '#6b7280' },
  infoValue: { fontSize: 14, color: '#1f2937', fontWeight: '500' },
  logoutBtn: { borderWidth: 2, borderColor: '#ef4444', borderRadius: 10, padding: 14, alignItems: 'center' },
  logoutText: { color: '#ef4444', fontSize: 16, fontWeight: 'bold' },
});
