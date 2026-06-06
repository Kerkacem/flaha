import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert, ActivityIndicator,
} from 'react-native';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';

export default function EditProfileScreen({ navigation }: any) {
  const { farmer, refreshProfile } = useAuth();
  const [name, setName] = useState(farmer?.name || '');
  const [wilaya, setWilaya] = useState(farmer?.wilaya || '');
  const [commune, setCommune] = useState(farmer?.commune || '');
  const [landHectares, setLandHectares] = useState(String(farmer?.land_hectares || ''));
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.put('/api/v1/farmer/profile', {
        name, wilaya, commune, land_hectares: landHectares ? parseFloat(landHectares) : null,
      });
      await refreshProfile?.();
      Alert.alert('تم', 'تم تحديث الملف الشخصي');
      navigation.goBack();
    } catch (err: any) {
      Alert.alert('خطأ', err?.response?.data?.detail || 'فشل التحديث');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.label}>الاسم</Text>
      <TextInput style={styles.input} value={name} onChangeText={setName} />

      <Text style={styles.label}>الولاية</Text>
      <TextInput style={styles.input} value={wilaya} onChangeText={setWilaya} />

      <Text style={styles.label}>البلدية</Text>
      <TextInput style={styles.input} value={commune} onChangeText={setCommune} />

      <Text style={styles.label}>مساحة الأرض (هكتار)</Text>
      <TextInput style={styles.input} value={landHectares} onChangeText={setLandHectares} keyboardType="numeric" />

      <TouchableOpacity style={styles.saveBtn} onPress={handleSave} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.saveBtnText}>حفظ</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16 },
  label: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 16 },
  input: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 14, fontSize: 15, color: '#1f2937' },
  saveBtn: { backgroundColor: '#16a34a', borderRadius: 10, padding: 14, alignItems: 'center', marginTop: 24 },
  saveBtnText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
