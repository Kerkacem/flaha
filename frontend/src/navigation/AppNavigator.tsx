import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StyleSheet } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import MarketplaceScreen from '../screens/MarketplaceScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import CreateProductScreen from '../screens/CreateProductScreen';
import WeatherScreen from '../screens/WeatherScreen';
import AdvisoryScreen from '../screens/AdvisoryScreen';
import ProfileScreen from '../screens/ProfileScreen';
import GovSupportScreen from '../screens/GovSupportScreen';
import TransactionHistoryScreen from '../screens/TransactionHistoryScreen';
import EditProfileScreen from '../screens/EditProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function TabIcon({ label, focused }: { label: string; focused: boolean }) {
  const icon: Record<string, string> = {
    الرئيسية: '🏠',
    السوق: '🛒',
    استشارة: '💬',
    الطقس: '🌤️',
    حسابي: '👤',
  };
  return (
    <View style={tabStyles.iconContainer}>
      <Text style={[tabStyles.icon, focused && tabStyles.iconFocused]}>{icon[label] || '📋'}</Text>
    </View>
  );
}

const tabStyles = StyleSheet.create({
  iconContainer: { alignItems: 'center', justifyContent: 'center' },
  icon: { fontSize: 22, opacity: 0.5 },
  iconFocused: { opacity: 1 },
});

function HomeTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused }) => <TabIcon label={route.name} focused={focused} />,
        tabBarActiveTintColor: '#16a34a',
        tabBarInactiveTintColor: '#9ca3af',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: 4,
          height: 60,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
      })}
    >
      <Tab.Screen name="الرئيسية" component={HomeScreen} />
      <Tab.Screen name="السوق" component={MarketplaceScreen} />
      <Tab.Screen name="استشارة" component={AdvisoryScreen} />
      <Tab.Screen name="الطقس" component={WeatherScreen} />
      <Tab.Screen name="حسابي" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { loading, token } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: '#16a34a' },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: 'bold' },
          headerBackTitle: 'رجوع',
        }}
      >
        {token ? (
          <>
            <Stack.Screen name="Home" component={HomeTabs} options={{ headerShown: false }} />
            <Stack.Screen name="ProductDetail" component={ProductDetailScreen} options={{ title: 'تفاصيل المنتج' }} />
            <Stack.Screen name="CreateProduct" component={CreateProductScreen} options={{ title: 'إضافة منتج' }} />
            <Stack.Screen name="GovSupport" component={GovSupportScreen} options={{ title: 'الدعم الحكومي' }} />
            <Stack.Screen name="TransactionHistory" component={TransactionHistoryScreen} options={{ title: 'سجل المعاملات' }} />
            <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: 'تعديل الملف الشخصي' }} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: false }} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
