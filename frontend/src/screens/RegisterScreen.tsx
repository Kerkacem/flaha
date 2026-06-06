import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, Alert, ScrollView,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

const WILAYAS = [
  'أدرار', 'الشلف', 'الأغواط', 'أم البواقي', 'باتنة', 'بجاية',
  'بسكرة', 'بشار', 'البليدة', 'البويرة', 'تمنراست', 'تبسة',
  'تلمسان', 'تيارت', 'تيزي وزو', 'الجزائر', 'الجلفة', 'جيجل',
  'سطيف', 'سعيدة', 'سكيكدة', 'سيدي بلعباس', 'عنابة', 'قالمة',
  'قسنطينة', 'المدية', 'مستغانم', 'المسيلة', 'معسكر', 'ورقلة',
  'وهران', 'البيض', 'إليزي', 'برج بوعريريج', 'بومرداس', 'الطارف',
  'تندوف', 'تسمسيلت', 'الوادي', 'خنشلة', 'سوق أهراس', 'تيبازة',
  'ميلة', 'عين الدفلى', 'النعامة', 'عين تموشنت', 'غرداية',
  'غليزان',
  'تيميمون', 'برج باجي مختار', 'أولاد جلال', 'بني عباس',
  'عين صالح', 'عين قزام', 'المغير', 'المنيعة', 'جانت', 'تقرت',
];

export default function RegisterScreen({ navigation, route }: any) {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState(route?.params?.phone || '+213');
  const [wilaya, setWilaya] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!name || !phone || !wilaya) {
      Alert.alert('خطأ', 'الرجاء ملء جميع الحقول');
      return;
    }
    setLoading(true);
    try {
      await register(phone, name, wilaya);
    } catch (err: any) {
      Alert.alert('خطأ في التسجيل', err?.response?.data?.detail || 'يرجى المحاولة مرة أخرى');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.logo}>🌱</Text>
          <Text style={styles.title}>تسجيل جديد</Text>
          <Text style={styles.subtitle}>انضم لعائلة فلاحة</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.fieldLabel}>الاسم الكامل</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="الاسم واللقب"
          />

          <Text style={styles.fieldLabel}>رقم الهاتف</Text>
          <TextInput
            style={styles.input}
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
          />

          <Text style={styles.fieldLabel}>الولاية</Text>
          <ScrollView style={styles.wilayaList} nestedScrollEnabled>
            {WILAYAS.map((w) => (
              <TouchableOpacity
                key={w}
                style={[styles.wilayaItem, wilaya === w && styles.wilayaSelected]}
                onPress={() => setWilaya(w)}
              >
                <Text style={[styles.wilayaText, wilaya === w && styles.wilayaTextSelected]}>{w}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={handleRegister} disabled={loading}>
            <Text style={styles.buttonText}>{loading ? 'جاري التسجيل...' : 'تسجيل'}</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Text style={styles.link}>عندي حساب؟ دخول</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  scroll: { flexGrow: 1, padding: 20 },
  header: { alignItems: 'center', marginBottom: 24, marginTop: 40 },
  logo: { fontSize: 48, marginBottom: 8 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#16a34a' },
  subtitle: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 24, elevation: 4, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8 },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 14, fontSize: 16, color: '#1f2937', backgroundColor: '#f9fafb' },
  wilayaList: { maxHeight: 180, borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 4 },
  wilayaItem: { padding: 10, borderRadius: 8, marginVertical: 1 },
  wilayaSelected: { backgroundColor: '#dcfce7' },
  wilayaText: { fontSize: 14, color: '#374151' },
  wilayaTextSelected: { color: '#16a34a', fontWeight: 'bold' },
  button: { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 20 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  link: { color: '#16a34a', textAlign: 'center', marginTop: 16, fontSize: 14 },
});
