import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert, ActivityIndicator, Image,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { AdvisoryResponse } from '../types';

const QUICK_QUERIES = [
  'متى نزرع الطماطم؟',
  'كيف نكافح البياض الدقيقي؟',
  'ما هي أفضل أنواع الأسمدة للقمح؟',
  'كيف نحمي المحاصيل من الصقيع؟',
];

export default function AdvisoryScreen() {
  const { farmer } = useAuth();
  const [query, setQuery] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [response, setResponse] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.7,
      base64: true,
    });
    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleQuery = async (text?: string) => {
    const q = text || query;
    if (!q.trim()) {
      Alert.alert('خطأ', 'الرجاء كتابة سؤالك');
      return;
    }
    setLoading(true);
    setResponse(null);
    try {
      const { data } = await api.post<AdvisoryResponse>('/api/v1/advisory/query', {
        farmer_phone: farmer?.phone || '+213000000000',
        query: q,
        image_base64: image || undefined,
      });
      setResponse(data);
    } catch (err: any) {
      Alert.alert('خطأ', err?.response?.data?.detail || 'تعذر الحصول على إجابة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <View style={styles.card}>
        <Text style={styles.title}>💬 اسأل فلاحة</Text>
        <Text style={styles.subtitle}>الاستشارة الفلاحية الذكية</Text>

        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
          placeholder="اكتب سؤالك الفلاحي هنا..."
          multiline
          numberOfLines={3}
        />

        <TouchableOpacity style={styles.imagePickerBtn} onPress={pickImage}>
          <Text style={styles.imagePickerText}>{image ? '🖼️ تم اختيار صورة' : '📷 أضف صورة'}</Text>
        </TouchableOpacity>
        {image && (
          <Image source={{ uri: image }} style={styles.previewImage} />
        )}

        <TouchableOpacity style={styles.button} onPress={() => handleQuery()} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>اسأل</Text>
          )}
        </TouchableOpacity>

        <Text style={styles.quickLabel}>أسئلة سريعة:</Text>
        <View style={styles.quickRow}>
          {QUICK_QUERIES.map((q) => (
            <TouchableOpacity key={q} style={styles.quickChip} onPress={() => { setQuery(q); handleQuery(q); }}>
              <Text style={styles.quickText}>{q}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {response && (
        <View style={styles.responseCard}>
          <Text style={styles.responseTitle}>الإجابة:</Text>
          <Text style={styles.responseText}>{response.response}</Text>
          {response.confidence != null && (
            <Text style={styles.confidence}>نسبة الثقة: {(response.confidence * 100).toFixed(0)}%</Text>
          )}
          {response.disease && (
            <View style={styles.diseaseBox}>
              <Text style={styles.diseaseTitle}>المرض المشخص: {response.disease}</Text>
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16, paddingBottom: 40 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, elevation: 4 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#1f2937' },
  subtitle: { fontSize: 14, color: '#6b7280', marginTop: 4, marginBottom: 16 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 14, fontSize: 15, color: '#1f2937', backgroundColor: '#f9fafb', minHeight: 80, textAlignVertical: 'top' },
  imagePickerBtn: { backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#16a34a', borderRadius: 10, padding: 12, alignItems: 'center', marginTop: 12, borderStyle: 'dashed' },
  imagePickerText: { color: '#16a34a', fontSize: 14, fontWeight: '600' },
  previewImage: { width: '100%', height: 160, borderRadius: 10, marginTop: 8, resizeMode: 'cover' },
  button: { backgroundColor: '#3b82f6', borderRadius: 10, padding: 14, alignItems: 'center', marginTop: 12 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  quickLabel: { fontSize: 14, fontWeight: '600', color: '#374151', marginTop: 16, marginBottom: 8 },
  quickRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  quickChip: { backgroundColor: '#eff6ff', paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#bfdbfe' },
  quickText: { fontSize: 12, color: '#2563eb' },
  responseCard: { backgroundColor: '#fff', borderRadius: 16, padding: 20, marginTop: 16, elevation: 4, borderLeftWidth: 4, borderLeftColor: '#3b82f6' },
  responseTitle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937', marginBottom: 8 },
  responseText: { fontSize: 15, color: '#374151', lineHeight: 24 },
  confidence: { fontSize: 12, color: '#9ca3af', marginTop: 12 },
  diseaseBox: { backgroundColor: '#fef2f2', borderRadius: 8, padding: 12, marginTop: 12 },
  diseaseTitle: { fontSize: 14, fontWeight: '600', color: '#dc2626' },
});
