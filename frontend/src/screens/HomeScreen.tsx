import React from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { StatCard } from '../components/StatCard';

const QUICK_ACTIONS = [
  { icon: 'storefront' as const, label: 'السوق', screen: 'السوق', color: '#f59e0b' },
  { icon: 'chatbubbles' as const, label: 'استشارة', screen: 'استشارة', color: '#3b82f6' },
  { icon: 'partly-sunny' as const, label: 'الطقس', screen: 'الطقس', color: '#06b6d4' },
  { icon: 'shield-checkmark' as const, label: 'الدعم الحكومي', screen: 'GovSupport', color: '#8b5cf6' },
];

export default function HomeScreen({ navigation }: any) {
  const { farmer } = useAuth();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.greeting}>
        <Text style={styles.greetingText}>مرحباً {farmer?.name || 'الفلاح'}</Text>
        <Text style={styles.wilaya}>{farmer?.wilaya || ''}</Text>
      </View>

      {farmer && (
        <View style={styles.statsRow}>
          <StatCard icon="star" label="التقييم" value={farmer.rating_avg?.toFixed(1) || '0.0'} />
          <StatCard icon="swap-horizontal" label="الصفقات" value={farmer.total_transactions || 0} color="#3b82f6" />
          {farmer.credit_score != null && (
            <StatCard icon="trending-up" label="الائتمان" value={farmer.credit_score} color="#f59e0b" />
          )}
        </View>
      )}

      <Text style={styles.sectionTitle}>خدمات سريعة</Text>
      <View style={styles.actionsGrid}>
        {QUICK_ACTIONS.map((action) => (
          <TouchableOpacity
            key={action.screen}
            style={styles.actionCard}
            onPress={() => navigation.navigate(action.screen)}
          >
            <View style={[styles.actionIcon, { backgroundColor: action.color + '20' }]}>
              <Text style={[styles.actionEmoji]}>
                {action.icon === 'storefront' ? '🛒' :
                 action.icon === 'chatbubbles' ? '💬' :
                 action.icon === 'partly-sunny' ? '🌤️' : '🏛️'}
              </Text>
            </View>
            <Text style={styles.actionLabel}>{action.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.sectionTitle}>معلومات سريعة</Text>
      <View style={styles.infoCard}>
        <Text style={styles.infoText}>
          تطبيق فلاحة هو مساعدك الفلاحي الذكي. يوفر لك:
        </Text>
        <Text style={styles.bullet}>• بيع وشراء المنتجات الفلاحية</Text>
        <Text style={styles.bullet}>• استشارات فلاحية ذكية</Text>
        <Text style={styles.bullet}>• متابعة أحوال الطقس</Text>
        <Text style={styles.bullet}>• دعم حكومي وقروض</Text>
        <Text style={styles.bullet}>• توصيل المنتجات</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16, paddingBottom: 32 },
  greeting: { marginBottom: 16 },
  greetingText: { fontSize: 24, fontWeight: 'bold', color: '#1f2937' },
  wilaya: { fontSize: 14, color: '#6b7280', marginTop: 2 },
  statsRow: { flexDirection: 'row', marginBottom: 24 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#1f2937', marginBottom: 12 },
  actionsGrid: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 24 },
  actionCard: {
    width: '48%', backgroundColor: '#fff', borderRadius: 12, padding: 16,
    alignItems: 'center', margin: '1%', elevation: 2, shadowColor: '#000',
    shadowOpacity: 0.1, shadowRadius: 4,
  },
  actionIcon: { width: 52, height: 52, borderRadius: 26, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  actionEmoji: { fontSize: 26 },
  actionLabel: { fontSize: 14, fontWeight: '600', color: '#1f2937' },
  infoCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, elevation: 2 },
  infoText: { fontSize: 14, color: '#374151', marginBottom: 8, lineHeight: 22 },
  bullet: { fontSize: 13, color: '#6b7280', lineHeight: 22, paddingLeft: 8 },
});
