import React, { useState, useCallback } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity, TextInput, Alert, ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const BANKS = ['BADR', 'CPA', 'BNA', 'CNMA'];
const PROGRAM_CODES = ['FNDIA', 'FGVA', 'دعم المدخلات', 'التأمين الفلاحي (CNA)', 'الفلاحة التضامنية'];

export default function GovSupportScreen() {
  const { farmer } = useAuth();
  const [activeTab, setActiveTab] = useState<'credit' | 'loan' | 'programs'>('credit');
  const [creditScore, setCreditScore] = useState<any>(null);
  const [programs, setPrograms] = useState<any[]>([]);
  const [deadlines, setDeadlines] = useState<any[]>([]);
  const [loanAmount, setLoanAmount] = useState('');
  const [loanBank, setLoanBank] = useState('BADR');
  const [loanPurpose, setLoanPurpose] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useFocusEffect(useCallback(() => {
    if (farmer) {
      api.get(`/api/v1/gov-support/farmers/${farmer.id}/credit-score`).then(({ data }) => setCreditScore(data)).catch(() => {});
    }
    Promise.all(PROGRAM_CODES.map((code) => api.get(`/api/v1/gov-support/programs/${encodeURIComponent(code)}`).then((r) => r.data).catch(() => null)))
      .then(setPrograms)
      .catch(() => {});
    api.get('/api/v1/gov-support/programs/check-deadlines').then(({ data }) => setDeadlines(data.deadlines || [])).catch(() => {});
  }, [farmer]));

  const handleLoanApply = async () => {
    if (!loanAmount || !loanPurpose) {
      Alert.alert('خطأ', 'الرجاء ملء جميع الحقول');
      return;
    }
    setSubmitting(true);
    try {
      const { data } = await api.post('/api/v1/gov-support/loans/apply', {
        farmer_phone: farmer?.phone,
        bank: loanBank,
        amount: parseFloat(loanAmount),
        purpose: loanPurpose,
      });
      Alert.alert('تم تقديم الطلب', `رقم الطلب: ${data.loan_id || data.id}`);
    } catch (err: any) {
      Alert.alert('خطأ', err?.response?.data?.detail || 'فشل تقديم الطلب');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.tabRow}>
        {(['credit', 'loan', 'programs'] as const).map((tab) => (
          <TouchableOpacity
            key={tab} style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
              {tab === 'credit' ? 'الائتمان' : tab === 'loan' ? 'القروض' : 'البرامج'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {activeTab === 'credit' && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>🏦 درجة الائتمان الفلاحي</Text>
            {creditScore ? (
              <>
                <Text style={styles.scoreValue}>{creditScore.score ?? creditScore.flaha_score ?? '--'}</Text>
                <Text style={styles.scoreLabel}>من 100</Text>
                <Text style={styles.scoreDesc}>{creditScore.level || ''}</Text>
              </>
            ) : (
              <Text style={styles.loadingText}>جاري تحميل المعلومات...</Text>
            )}
          </View>
        )}

        {activeTab === 'loan' && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>💰 طلب قرض فلاحي</Text>
            <Text style={styles.fieldLabel}>البنك</Text>
            <View style={styles.bankRow}>
              {BANKS.map((b) => (
                <TouchableOpacity key={b} style={[styles.bankChip, loanBank === b && styles.bankActive]} onPress={() => setLoanBank(b)}>
                  <Text style={[styles.bankText, loanBank === b && styles.bankTextActive]}>{b}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <Text style={styles.fieldLabel}>المبلغ (د.ج)</Text>
            <TextInput style={styles.input} value={loanAmount} onChangeText={setLoanAmount} keyboardType="decimal-pad" placeholder="مثال: 500000" />
            <Text style={styles.fieldLabel}>الغرض من القرض</Text>
            <TextInput style={styles.input} value={loanPurpose} onChangeText={setLoanPurpose} placeholder="مثال: شراء بذور وأسمدة" />
            <TouchableOpacity style={styles.button} onPress={handleLoanApply} disabled={submitting}>
              {submitting ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>تقديم الطلب</Text>}
            </TouchableOpacity>
          </View>
        )}

        {activeTab === 'programs' && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>📋 البرامج الحكومية</Text>
            {programs.filter(Boolean).length === 0 ? (
              <Text style={styles.loadingText}>جاري تحميل البرامج...</Text>
            ) : (
              programs.filter(Boolean).map((prog: any, i: number) => (
                <View key={i} style={styles.programItem}>
                  <Text style={styles.programTitle}>🔹 {prog.name || prog.program}</Text>
                  <Text style={styles.programDesc}>{prog.description}</Text>
                  {prog.max_amount_dzd && (
                    <Text style={styles.programMeta}>💰 حتى {prog.max_amount_dzd.toLocaleString()} د.ج</Text>
                  )}
                </View>
              ))
            )}
            {deadlines.length > 0 && (
              <>
                <Text style={[styles.cardTitle, { marginTop: 20 }]}>⏰ المواعيد النهائية</Text>
                {deadlines.map((d: any, i: number) => (
                  <View key={i} style={styles.programItem}>
                    <Text style={styles.programTitle}>{d.program}</Text>
                    <Text style={styles.programDesc}>{d.description}</Text>
                  </View>
                ))}
              </>
            )}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  tabRow: { flexDirection: 'row', backgroundColor: '#fff', padding: 8, margin: 12, borderRadius: 12, elevation: 2 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 8, alignItems: 'center' },
  tabActive: { backgroundColor: '#16a34a' },
  tabText: { fontSize: 14, fontWeight: '600', color: '#6b7280' },
  tabTextActive: { color: '#fff' },
  content: { padding: 16 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 20, elevation: 4 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', color: '#1f2937', marginBottom: 16 },
  loadingText: { fontSize: 14, color: '#6b7280', textAlign: 'center', marginTop: 20 },
  scoreValue: { fontSize: 48, fontWeight: 'bold', color: '#16a34a', textAlign: 'center' },
  scoreLabel: { fontSize: 14, color: '#9ca3af', textAlign: 'center' },
  scoreDesc: { fontSize: 14, color: '#374151', marginTop: 12, lineHeight: 22, textAlign: 'center' },
  fieldLabel: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#d1d5db', borderRadius: 10, padding: 14, fontSize: 15, color: '#1f2937', backgroundColor: '#f9fafb' },
  bankRow: { flexDirection: 'row', gap: 8 },
  bankChip: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 10, backgroundColor: '#f3f4f6' },
  bankActive: { backgroundColor: '#16a34a' },
  bankText: { fontSize: 14, fontWeight: '600', color: '#374151' },
  bankTextActive: { color: '#fff' },
  button: { backgroundColor: '#16a34a', borderRadius: 10, padding: 16, alignItems: 'center', marginTop: 20 },
  buttonText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },

  programItem: { backgroundColor: '#f0fdf4', borderRadius: 8, padding: 12, marginTop: 8 },
  programTitle: { fontSize: 14, fontWeight: '600', color: '#1f2937' },
  programDesc: { fontSize: 13, color: '#6b7280', marginTop: 4 },
  programMeta: { fontSize: 12, color: '#16a34a', marginTop: 4 },
});
