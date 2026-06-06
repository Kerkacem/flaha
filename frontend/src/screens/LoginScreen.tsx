import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, Alert, ScrollView,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

export default function LoginScreen({ navigation }: any) {
  const { login } = useAuth();
  const [phone, setPhone] = useState('+213');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!phone || phone.length < 10) {
      Alert.alert('خطأ', 'الرجاء إدخال رقم الهاتف');
      return;
    }
    setLoading(true);
    try {
      const res = await login(phone, otp);
      if (res.is_new) {
        navigation.replace('Register', { phone });
      }
    } catch (err: any) {
      Alert.alert('خطأ في تسجيل الدخول', err?.response?.data?.detail || 'يرجى المحاولة مرة أخرى');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.logo}>🌾</Text>
          <Text style={styles.title}>فلاحة</Text>
          <Text style={styles.subtitle}>الوكيل الفلاحي الذكي</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.fieldLabel}>رقم الهاتف</Text>
          <TextInput
            style={styles.input}
            value={phone}
            onChangeText={setPhone}
            placeholder="+213XXXXXXXXX"
            keyboardType="phone-pad"
            autoComplete="tel"
          />

          <Text style={styles.fieldLabel}>رمز التحقق (اختياري)</Text>
          <TextInput
            style={styles.input}
            value={otp}
            onChangeText={setOtp}
            placeholder="أدخل الرمز أو اتركه فارغاً"
            keyboardType="number-pad"
            maxLength={6}
          />

          <TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={handleLogin} disabled={loading}>
            <Text style={styles.buttonText}>{loading ? 'جاري تسجيل الدخول...' : 'دخول'}</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.link}>ماعنديش حساب؟ سجل هنا</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  scroll: { flexGrow: 1, justifyContent: 'center', padding: 20 },
  header: { alignItems: 'center', marginBottom: 32 },
  logo: { fontSize: 64, marginBottom: 8 },
  title: { fontSize: 36, fontWeight: 'bold', color: '#16a34a' },
  subtitle: { fontSize: 16, color: '#6b7280', marginTop: 4 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 24, elevation: 4, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 8 },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 14, fontSize: 16, color: '#1f2937', backgroundColor: '#f9fafb' },
  button: { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 24 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  link: { color: '#16a34a', textAlign: 'center', marginTop: 16, fontSize: 14 },
});
