import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert,
} from 'react-native';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const CATEGORIES = ['خضار', 'فواكه', 'حبوب', 'زيت', 'عسل', 'توابل', 'تمر', 'ألبان', 'لحوم'];
const UNITS = ['كغ', 'لتر', 'قنطار', 'وحدة', 'صندوق'];

export default function CreateProductScreen({ navigation }: any) {
  const { farmer } = useAuth();
  const [name, setName] = useState('');
  const [category, setCategory] = useState('خضار');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('كغ');
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');
  const [isOrganic, setIsOrganic] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!name || !quantity || !price) {
      Alert.alert('خطأ', 'الرجاء ملء الحقول الأساسية');
      return;
    }
    setSubmitting(true);
    try {
      await api.post('/api/v1/marketplace/products', {
        farmer_phone: farmer?.phone,
        name,
        category,
        description: description || undefined,
        quantity: parseFloat(quantity),
        unit,
        price: parseFloat(price),
        wilaya: farmer?.wilaya,
        is_organic: isOrganic,
      });
      Alert.alert('تم!', 'تم إضافة المنتج بنجاح');
      navigation.goBack();
    } catch (err: any) {
      Alert.alert('خطأ', err?.response?.data?.detail || 'فشل إضافة المنتج');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <Text style={styles.fieldLabel}>اسم المنتج</Text>
        <TextInput style={styles.input} value={name} onChangeText={setName} placeholder="مثال: طماطم" />

        <Text style={styles.fieldLabel}>الفئة</Text>
        <View style={styles.chipRow}>
          {CATEGORIES.map((c) => (
            <TouchableOpacity
              key={c} style={[styles.chip, category === c && styles.chipActive]}
              onPress={() => setCategory(c)}
            >
              <Text style={[styles.chipText, category === c && styles.chipTextActive]}>{c}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.row}>
          <View style={{ flex: 1 }}>
            <Text style={styles.fieldLabel}>الكمية</Text>
            <TextInput style={styles.input} value={quantity} onChangeText={setQuantity} keyboardType="decimal-pad" />
          </View>
          <View style={{ flex: 1, marginLeft: 8 }}>
            <Text style={styles.fieldLabel}>الوحدة</Text>
            <View style={styles.chipRow}>
              {UNITS.map((u) => (
                <TouchableOpacity
                  key={u} style={[styles.chipSm, unit === u && styles.chipActive]}
                  onPress={() => setUnit(u)}
                >
                  <Text style={[styles.chipTextSm, unit === u && styles.chipTextActive]}>{u}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <Text style={styles.fieldLabel}>السعر (د.ج)</Text>
        <TextInput style={styles.input} value={price} onChangeText={setPrice} keyboardType="decimal-pad" placeholder="مثال: 120" />

        <Text style={styles.fieldLabel}>الوصف (اختياري)</Text>
        <TextInput style={[styles.input, styles.textArea]} value={description} onChangeText={setDescription} multiline numberOfLines={3} />

        <TouchableOpacity style={styles.checkRow} onPress={() => setIsOrganic(!isOrganic)}>
          <View style={[styles.checkbox, isOrganic && styles.checkboxActive]}>
            {isOrganic && <Text style={styles.checkmark}>✓</Text>}
          </View>
          <Text style={styles.checkLabel}>منتج عضوي</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={submitting}>
          <Text style={styles.buttonText}>{submitting ? 'جاري النشر...' : 'نشر المنتج'}</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16, paddingBottom: 40 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, elevation: 4 },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 14 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 12, fontSize: 15, color: '#1f2937', backgroundColor: '#f9fafb' },
  textArea: { minHeight: 80, textAlignVertical: 'top' },
  row: { flexDirection: 'row' },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: '#f3f4f6' },
  chipActive: { backgroundColor: '#16a34a' },
  chipText: { fontSize: 13, color: '#374151' },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  chipSm: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, backgroundColor: '#f3f4f6', marginVertical: 2 },
  chipTextSm: { fontSize: 12, color: '#374151' },
  checkRow: { flexDirection: 'row', alignItems: 'center', marginTop: 16 },
  checkbox: { width: 24, height: 24, borderRadius: 6, borderWidth: 2, borderColor: '#d1d5db', justifyContent: 'center', alignItems: 'center' },
  checkboxActive: { backgroundColor: '#16a34a', borderColor: '#16a34a' },
  checkmark: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
  checkLabel: { marginLeft: 10, fontSize: 14, color: '#374151' },
  button: { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 24 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
});
