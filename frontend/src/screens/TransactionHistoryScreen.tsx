import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { Transaction } from '../types';

export default function TransactionHistoryScreen() {
  const { farmer } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get<Transaction[]>('/api/v1/transactions', {
          params: { farmer_id: farmer?.id },
        });
        setTransactions(data);
      } catch {
        setTransactions([]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <ActivityIndicator size="large" color="#16a34a" style={{ marginTop: 40 }} />;
  }

  if (transactions.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>لا توجد معاملات بعد</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={transactions}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.list}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.productName}>{item.product_name}</Text>
          <Text style={styles.detail}>البائع: {item.seller_name}</Text>
          <Text style={styles.detail}>المشتري: {item.buyer_name}</Text>
          <Text style={styles.detail}>الكمية: {item.quantity}</Text>
          <Text style={styles.detail}>السعر: {item.total_price} د.ج</Text>
          <View style={styles.statusRow}>
            <Text style={[styles.badge, item.delivery_status === 'delivered' ? styles.delivered : styles.pending]}>
              {item.delivery_status === 'delivered' ? 'تم التوصيل' : 'قيد التوصيل'}
            </Text>
            <Text style={[styles.badge, item.payment_status === 'paid' ? styles.paid : styles.unpaid]}>
              {item.payment_status === 'paid' ? 'مدفوع' : 'غير مدفوع'}
            </Text>
          </View>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  list: { padding: 16 },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  emptyText: { fontSize: 16, color: '#6b7280' },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, elevation: 2 },
  productName: { fontSize: 16, fontWeight: 'bold', color: '#1f2937', marginBottom: 8 },
  detail: { fontSize: 13, color: '#4b5563', marginBottom: 4 },
  statusRow: { flexDirection: 'row', marginTop: 8, gap: 8 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, fontSize: 12, fontWeight: '600' },
  delivered: { backgroundColor: '#dcfce7', color: '#16a34a' },
  pending: { backgroundColor: '#fef3c7', color: '#d97706' },
  paid: { backgroundColor: '#dcfce7', color: '#16a34a' },
  unpaid: { backgroundColor: '#fef2f2', color: '#dc2626' },
});
