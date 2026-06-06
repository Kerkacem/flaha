import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';
import api from '../api/client';
import { useAuth } from '../contexts/AuthContext';

const WILAYA_MAP: Record<string, string> = {
  'أدرار': 'Adrar', 'الشلف': 'Chlef', 'الأغواط': 'Laghouat', 'أم البواقي': 'Oum El Bouaghi',
  'باتنة': 'Batna', 'بجاية': 'Bejaia', 'بسكرة': 'Biskra', 'بشار': 'Bechar',
  'البليدة': 'Blida', 'البويرة': 'Bouira', 'تمنراست': 'Tamanrasset', 'تبسة': 'Tebessa',
  'تلمسان': 'Tlemcen', 'تيارت': 'Tiaret', 'تيزي وزو': 'Tizi Ouzou', 'الجزائر': 'Algiers',
  'الجلفة': 'Djelfa', 'جيجل': 'Jijel', 'سطيف': 'Setif', 'سعيدة': 'Saida',
  'سكيكدة': 'Skikda', 'سيدي بلعباس': 'Sidi Bel Abbes', 'عنابة': 'Annaba', 'قالمة': 'Guelma',
  'قسنطينة': 'Constantine', 'المدية': 'Medea', 'مستغانم': 'Mostaganem', 'المسيلة': "M'Sila",
  'معسكر': 'Mascara', 'ورقلة': 'Ouargla', 'وهران': 'Oran', 'البيض': 'El Bayadh',
  'إليزي': 'Illizi', 'برج بوعريريج': 'Bordj Bou Arreridj', 'بومرداس': 'Boumerdes',
  'الطارف': 'El Tarf', 'تندوف': 'Tindouf', 'تسمسيلت': 'Tissemsilt', 'الوادي': 'El Oued',
  'خنشلة': 'Khenchela', 'سوق أهراس': 'Souk Ahras', 'تيبازة': 'Tipaza', 'ميلة': 'Mila',
  'عين الدفلى': 'Ain Defla', 'النعامة': 'Naama', 'عين تموشنت': 'Ain Temouchent',
  'غرداية': 'Ghardaia', 'غليزان': 'Relizane',
  'تيميمون': 'Timimoun', 'برج باجي مختار': 'Bordj Badji Mokhtar', 'أولاد جلال': 'Ouled Djellal',
  'بني عباس': 'Beni Abbes', 'عين صالح': 'In Salah', 'عين قزام': 'In Guezzam',
  'المغير': 'El M\'Ghair', 'المنيعة': 'El Menia', 'جانت': 'Djanet', 'تقرت': 'Touggourt',
};

export default function WeatherScreen() {
  const { farmer } = useAuth();
  const [weather, setWeather] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const wilaya = farmer?.wilaya || 'الجزائر';

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get('/api/v1/weather/current', { params: { wilaya } });
        setWeather({ ...data, city: wilaya });
      } catch {
        setError('تعذر تحميل بيانات الطقس');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <View style={styles.centered}><ActivityIndicator size="large" color="#16a34a" /></View>;
  }

  if (error) {
    return (
      <View style={styles.centered}>
        <Text style={{ fontSize: 16, color: '#6b7280', textAlign: 'center' }}>{error}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.card}>
        <Text style={styles.city}>🌤️ {weather?.city || wilaya}</Text>
        <Text style={styles.temp}>{weather?.temperature ?? '--'}°C</Text>
        <Text style={styles.desc}>{weather?.description || 'طقس معتدل'}</Text>
        <View style={styles.details}>
          <View style={styles.detailItem}>
            <Text style={styles.detailValue}>{weather?.humidity ?? '--'}%</Text>
            <Text style={styles.detailLabel}>الرطوبة</Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailValue}>{weather?.wind_speed ?? '--'} كم/س</Text>
            <Text style={styles.detailLabel}>الرياح</Text>
          </View>
        </View>
      </View>

      <View style={styles.tip}>
        <Text style={styles.tipTitle}>💡 نصيحة فلاحية</Text>
        <Text style={styles.tipText}>
          {weather?.temperature && weather.temperature > 35
            ? 'احرص على ري المحاصيل في الصباح الباكر أو المساء'
            : 'الظروف مناسبة للعمل في الحقل'}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0fdf4' },
  content: { padding: 16 },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0fdf4' },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 24, alignItems: 'center', elevation: 4 },
  city: { fontSize: 20, fontWeight: '600', color: '#374151', marginBottom: 8 },
  temp: { fontSize: 56, fontWeight: 'bold', color: '#f59e0b' },
  desc: { fontSize: 16, color: '#6b7280', marginTop: 4 },
  details: { flexDirection: 'row', marginTop: 20, gap: 24 },
  detailItem: { alignItems: 'center' },
  detailValue: { fontSize: 20, fontWeight: 'bold', color: '#1f2937' },
  detailLabel: { fontSize: 12, color: '#9ca3af', marginTop: 4 },
  tip: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginTop: 16, elevation: 2 },
  tipTitle: { fontSize: 16, fontWeight: 'bold', color: '#1f2937', marginBottom: 8 },
  tipText: { fontSize: 14, color: '#374151', lineHeight: 22 },
});
