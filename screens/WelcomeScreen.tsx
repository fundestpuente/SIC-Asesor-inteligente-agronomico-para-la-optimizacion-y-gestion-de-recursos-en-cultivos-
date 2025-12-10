import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { COLORS } from '../constants/colors';

type WelcomeScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Welcome'
>;

interface Props {
  navigation: WelcomeScreenNavigationProp;
}

const FARMER_ID_KEY = '@agroia_farmer_id';

const WelcomeScreen: React.FC<Props> = ({ navigation }) => {
  const [farmerId, setFarmerId] = useState('');
  const [loading, setLoading] = useState(false); // Cambiado a false para mostrar siempre el onboarding

  // ⚠️ COMENTADO TEMPORALMENTE - Descomenta esto en producción para saltar el onboarding si ya hay un usuario
  // useEffect(() => {
  //   checkExistingFarmer();
  // }, []);

  // const checkExistingFarmer = async () => {
  //   try {
  //     const existingId = await AsyncStorage.getItem(FARMER_ID_KEY);
  //     if (existingId) {
  //       navigation.replace('Home');
  //     } else {
  //       setLoading(false);
  //     }
  //   } catch (error) {
  //     console.error('Error checking farmer ID:', error);
  //     setLoading(false);
  //   }
  // };

  const handleStart = async () => {
    const trimmed = farmerId.trim();
    if (!trimmed) {
      Alert.alert('Required', 'Please tell us your name');
      return;
    }

    try {
      await AsyncStorage.setItem(FARMER_ID_KEY, trimmed);
      navigation.replace('Home');
    } catch (error) {
      Alert.alert('Error', 'Could not save your name. Try again.');
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <Image source={require('../assets/start.png')} style={styles.icon} resizeMode="contain" />

        <Text style={styles.appName}>AgroMind</Text>
        <Text style={styles.subtitle}>Tell me your name</Text>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={farmerId}
            onChangeText={setFarmerId}
            placeholder="Tell me your name"
            placeholderTextColor={COLORS.textLight}
            autoCapitalize="words"
          />
        </View>

        <TouchableOpacity style={styles.button} onPress={handleStart} activeOpacity={0.9}>
          <Text style={styles.buttonText}>start</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFEF5',
  },
  center: { justifyContent: 'center', alignItems: 'center' },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  icon: {
    width: 120,
    height: 120,
    marginBottom: 20,
  },
  appName: {
    fontSize: 40,
    fontWeight: '700',
    color: COLORS.secondary,
    marginBottom: 8,
    fontFamily: 'Montserrat_700Bold',
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textLight,
    marginBottom: 24,
    fontFamily: 'Montserrat_500Medium',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
    paddingHorizontal: 24,
  },
  input: {
    backgroundColor: COLORS.white,
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    color: COLORS.text,
  },
  button: {
    backgroundColor: COLORS.secondary,
    paddingVertical: 14,
    paddingHorizontal: 48,
    borderRadius: 999,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: '700',
    fontFamily: 'Montserrat_700Bold',
  },
  loadingText: {
    fontSize: 16,
    color: COLORS.white,
  },
});

export default WelcomeScreen;
