import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import api from '../api/client';
import { Product } from '../types';
import { useAuth } from '../contexts/AuthContext';

export default function ProductDetailScreen({ route, navigation }: any) {
  const { farmer } = useAuth();
  const [product, setProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [buying, setBuying] = useState(false);
  const { productId } = route.params;

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get<Product>(`/api/v1/marketplace/products/${productId}`);
        setProduct(data);
      } catch {
        Alert.alert('خطأ', 'تعذر تحميل تفاصيل المنتج');
        navigation.goBack();
      }
    })();
  }, [productId]);

  const handleBuy = async () => {
    if (!farmer) {
      Alert.alert('تسجيل الدخول', 'الرجاء تسجيل الدخول أولاً');
      return;
    }
    setBuying(true);
    try {
      const { data } = await api.post('/api/v1/marketplace/transactions', {
        product_id: productId,
        buyer_phone: farmer.phone,
        quantity,
      });
      Alert.alert('تم!', `تم إنشاء الصفقة ${data.id}`);
      navigation.goBack();
    } catch (err: any) {
      Alert.alert('خطأ', err?.response?.data?.detail || 'فشلت عملية الشراء');
    } finally {
      setBuying(false);
    }
  };

  if (!product) {
    return (
      <View style={styles.container}>
        <Text style={styles.loading}>جاري التحميل...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.card}>
        <View style={styles.headerRow}>
          <Text style={styles.name}>{product.name}</Text>
          {product.is_organic && <Text style={styles.organic}>عضوي</Text>}
        </View>

        <Text style={styles.category}>{product.category}</Text>
        <Text style={styles.price}>{product.price} د.ج</Text>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>الكمية:</Text>
          <Text style={styles.detailValue}>{product.quantity} {product.unit}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>الولاية:</Text>
          <Text style={styles.detailValue}>{product.wilaya}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>الفلاح:</Text>
          <Text style={styles.detailValue}>{product.farmer_name}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>التقييم:</Text>
          <Text style={styles.detailValue}>⭐ {product.farmer_rating?.toFixed(1) || '0.0'}</Text>
        </View>

        {product.description && (
          <Text style={styles.description}>{product.description}</Text>
        )}

        {product.farmer_phone !== farmer?.phone && (
          <>
            <View style={styles.qtyRow}>
              <TouchableOpacity style={styles.qtyBtn} onPress={() => setQuantity((q) => Math.max(1, q - 1))}>
                <Text style={styles.qtyBtnText}>-</Text>
              </TouchableOpacity>
              <Text style={styles.qtyValue}>{quantity}</Text>
              <TouchableOpacity style={styles.qtyBtn} onPress={() => setQuantity((q) => q + 1)}>
                <Text style={styles.qtyBtnText}>+</Text>
              </TouchableOpacity>
              <Text style={styles.qtyUnit}>{product.unit}</Text>
            </View>
            <Text style={styles.totalPrice}>المجموع: {(quantity * product.price).toFixed(0)} د.ج</Text>
            <TouchableOpacity style={[styles.buyButton, buying && styles.buttonDisabled]} onPress={handleBuy} disabled={buying}>
              <Text style={styles.buyText}>{buying ? 'جاري الشراء...' : 'شراء'}</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16 },
  loading: { textAlign: 'center', marginTop: 60, fontSize: 16, color: '#6b7280' },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, elevation: 4 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  name: { fontSize: 24, fontWeight: 'bold', color: '#1f2937', flex: 1 },
  organic: { fontSize: 12, color: '#16a34a', backgroundColor: '#dcfce7', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  category: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  price: { fontSize: 32, fontWeight: 'bold', color: '#16a34a', marginTop: 16 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 12, paddingVertical: 8, borderTopWidth: 1, borderTopColor: '#f3f4f6' },
  detailLabel: { fontSize: 14, color: '#6b7280' },
  detailValue: { fontSize: 14, color: '#1f2937', fontWeight: '500' },
  description: { marginTop: 16, fontSize: 14, color: '#374151', lineHeight: 22 },
  qtyRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 20, gap: 12 },
  qtyBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#e5e7eb', justifyContent: 'center', alignItems: 'center' },
  qtyBtnText: { fontSize: 22, color: '#1f2937', fontWeight: 'bold' },
  qtyValue: { fontSize: 22, fontWeight: 'bold', color: '#1f2937', minWidth: 40, textAlign: 'center' },
  qtyUnit: { fontSize: 14, color: '#6b7280' },
  totalPrice: { fontSize: 20, fontWeight: 'bold', color: '#16a34a', textAlign: 'center', marginTop: 12 },
  buyButton: { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 12 },
  buyText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  buttonDisabled: { opacity: 0.6 },
});
