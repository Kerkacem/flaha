import React, { useState, useCallback } from 'react';
import {
  View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, RefreshControl, Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import api from '../api/client';
import { Product } from '../types';

const CATEGORIES = ['الكل', 'خضار', 'فواكه', 'حبوب', 'زيت', 'عسل', 'توابل', 'تمر', 'ألبان', 'لحوم'];

export default function MarketplaceScreen({ navigation }: any) {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('الكل');
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (category !== 'الكل') params.category = category;
      const { data } = await api.get('/api/v1/marketplace/products', { params });
      setProducts(data.products || []);
    } catch (err: any) {
      Alert.alert('خطأ', 'تعذر تحميل المنتجات');
    } finally {
      setLoading(false);
    }
  }, [category]);

  useFocusEffect(useCallback(() => { fetchProducts(); }, [fetchProducts]));

  const filteredProducts = search
    ? products.filter((p) => p.name.includes(search))
    : products;

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchProducts();
    setRefreshing(false);
  };

  const renderProduct = ({ item }: { item: Product }) => (
    <TouchableOpacity
      style={styles.productCard}
      onPress={() => navigation.navigate('ProductDetail', { productId: item.id })}
    >
      <View style={styles.productHeader}>
        <Text style={styles.productName}>{item.name}</Text>
        {item.is_organic && <Text style={styles.organicBadge}>عضوي</Text>}
      </View>
      <Text style={styles.productQuantity}>{item.quantity} {item.unit}</Text>
      <View style={styles.productFooter}>
        <Text style={styles.productPrice}>{item.price} د.ج</Text>
        <Text style={styles.productWilaya}>{item.wilaya}</Text>
      </View>
      <Text style={styles.productFarmer}>{item.farmer_name}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="ابحث عن منتج..."
        value={search}
        onChangeText={setSearch}
      />
      <FlatList
        horizontal
        showsHorizontalScrollIndicator={false}
        data={CATEGORIES}
        keyExtractor={(c) => c}
        style={styles.categoriesList}
        contentContainerStyle={styles.categoriesContent}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.categoryChip, category === item && styles.categoryActive]}
            onPress={() => setCategory(item)}
          >
            <Text style={[styles.categoryText, category === item && styles.categoryTextActive]}>{item}</Text>
          </TouchableOpacity>
        )}
      />
      {loading ? (
        <Text style={styles.empty}>جاري التحميل...</Text>
      ) : (
        <FlatList
          data={filteredProducts}
          keyExtractor={(p) => p.id}
          renderItem={renderProduct}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          contentContainerStyle={styles.list}
          numColumns={2}
          ListEmptyComponent={
            <Text style={styles.empty}>لا توجد منتجات متاحة حالياً</Text>
          }
        />
      )}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate('CreateProduct')}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  searchInput: { margin: 12, padding: 12, borderRadius: 10, backgroundColor: '#fff', fontSize: 15, borderWidth: 1, borderColor: '#d1d5db' },
  categoriesList: { maxHeight: 48 },
  categoriesContent: { paddingHorizontal: 12, gap: 8 },
  categoryChip: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: '#fff', marginRight: 8 },
  categoryActive: { backgroundColor: '#16a34a' },
  categoryText: { fontSize: 13, color: '#374151' },
  categoryTextActive: { color: '#fff', fontWeight: '600' },
  list: { padding: 8 },
  productCard: {
    flex: 1, backgroundColor: '#fff', borderRadius: 12, padding: 12, margin: 4,
    elevation: 2, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 4,
  },
  productHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  productName: { fontSize: 15, fontWeight: 'bold', color: '#1f2937', flex: 1 },
  organicBadge: { fontSize: 10, color: '#16a34a', backgroundColor: '#dcfce7', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  productQuantity: { fontSize: 13, color: '#6b7280', marginTop: 4 },
  productFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  productPrice: { fontSize: 16, fontWeight: 'bold', color: '#16a34a' },
  productWilaya: { fontSize: 12, color: '#9ca3af' },
  productFarmer: { fontSize: 11, color: '#9ca3af', marginTop: 4 },
  empty: { textAlign: 'center', color: '#9ca3af', marginTop: 60, fontSize: 16 },
  fab: {
    position: 'absolute', bottom: 20, right: 20, width: 56, height: 56,
    borderRadius: 28, backgroundColor: '#16a34a', justifyContent: 'center',
    alignItems: 'center', elevation: 6,
  },
  fabText: { fontSize: 28, color: '#fff', lineHeight: 30 },
});
