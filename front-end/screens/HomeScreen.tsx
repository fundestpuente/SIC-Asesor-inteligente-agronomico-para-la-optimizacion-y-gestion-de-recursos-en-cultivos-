import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ImageBackground,
  SafeAreaView,
  Platform,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { LinearGradient } from 'expo-linear-gradient';

type HomeScreenNavigationProp = NativeStackNavigationProp<
  RootStackParamList,
  'Home'
>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

const FARMER_ID_KEY = '@agroia_farmer_id';
const LOCATION_KEY = '@agroia_location';

const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const [userName, setUserName] = useState('');
  const [isCapturingLocation, setIsCapturingLocation] = useState(false);

  useEffect(() => {
    loadUserName();
  }, []);

  const loadUserName = async () => {
    try {
      const name = await AsyncStorage.getItem(FARMER_ID_KEY);
      if (name) {
        setUserName(name);
      }
    } catch (error) {
      console.error('Error loading user name:', error);
    }
  };

  const handleNewAnalysis = async () => {
    setIsCapturingLocation(true);
    
    try {
      // Verificar si ya tenemos permisos
      const { status: existingStatus } = await Location.getForegroundPermissionsAsync();
      
      let finalStatus = existingStatus;
      
      // Si no tenemos permisos, solicitarlos
      if (existingStatus !== 'granted') {
        // Mostrar mensaje explicativo antes de solicitar permisos
        Alert.alert(
          'Permiso de ubicación requerido',
          'AgroMind necesita acceso a tu ubicación para obtener datos climáticos precisos y realizar el análisis de tu cultivo.',
          [
            {
              text: 'Cancelar',
              style: 'cancel',
              onPress: () => {
                setIsCapturingLocation(false);
              }
            },
            {
              text: 'Permitir',
              onPress: async () => {
                const { status } = await Location.requestForegroundPermissionsAsync();
                finalStatus = status;
                
                if (status !== 'granted') {
                  Alert.alert(
                    'Permiso denegado',
                    'No se puede continuar sin acceso a la ubicación. Por favor, habilita los permisos de ubicación en la configuración de tu dispositivo para usar esta función.',
                    [{ text: 'Entendido' }]
                  );
                  setIsCapturingLocation(false);
                  return;
                }
                
                // Si se concedió el permiso, capturar ubicación
                await captureLocation();
              }
            }
          ]
        );
        return;
      }
      
      // Si ya tenemos permisos, capturar ubicación directamente
      await captureLocation();
      
    } catch (error) {
      console.error('Error in handleNewAnalysis:', error);
      Alert.alert(
        'Error',
        'Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente.'
      );
      setIsCapturingLocation(false);
    }
  };

  const captureLocation = async () => {
    try {
      // Capturar ubicación actual con alta precisión
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      const locationData = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        timestamp: new Date().toISOString(),
      };

      // Guardar ubicación en AsyncStorage
      await AsyncStorage.setItem(LOCATION_KEY, JSON.stringify(locationData));

      // Navegar a CropSelection
      navigation.navigate('CropSelection');
      
    } catch (error) {
      console.error('Error capturing location:', error);
      Alert.alert(
        'Error al obtener ubicación',
        'No se pudo obtener tu ubicación. Verifica que el GPS esté activado y que tengas buena señal.',
        [{ text: 'Reintentar', onPress: () => captureLocation() }]
      );
    } finally {
      setIsCapturingLocation(false);
    }
  };

  return (
    <ImageBackground
      source={require('../assets/images/analysis.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      {/* Overlay oscuro para mejorar legibilidad */}
      <View style={styles.overlay} />
      
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.container}>
          {/* Contenido central */}
          <View style={styles.centerContent}>
            <Image
              source={require('../assets/agricultura.png')}
              style={styles.logoIcon}
              resizeMode="contain"
            />
            <Text style={styles.appTitle}>AgroMind</Text>
            
            {userName && (
              <>
                <Text style={styles.welcomeText}>
                  ¡Bienvenido, {userName}!
                </Text>
                <Text style={styles.callToAction}>
                  Descubre recomendaciones inteligentes para tus cultivos
                </Text>
              </>
            )}

            {/* Botón principal gigante */}
            <TouchableOpacity
              style={styles.buttonWrapper}
              onPress={handleNewAnalysis}
              activeOpacity={0.85}
              disabled={isCapturingLocation}
            >
              <LinearGradient
                colors={isCapturingLocation ? ['#9E9E9E', '#BDBDBD'] : ['#4CAF50', '#66BB6A']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.gradientButton}
              >
                {isCapturingLocation ? (
                  <View style={styles.loadingContainer}>
                    <ActivityIndicator color="#FFFFFF" size="small" />
                    <Text style={styles.loadingText}>Capturando ubicación...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>Nuevo análisis</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>

          {/* Footer discreto */}
          <View style={styles.footerSection}>
            <Text style={styles.footerText}>
              v1.0 • Recomendaciones agronómicas inteligentes
            </Text>
          </View>
        </View>
      </SafeAreaView>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.35)', // Overlay oscuro semi-transparente
  },
  safeArea: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  container: {
    flex: 1,
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 20,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  logoIcon: {
    width: 90,
    height: 90,
    marginBottom: 16,
  },
  appTitle: {
    fontSize: 42,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 20,
    fontFamily: 'Montserrat_600SemiBold',
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
    fontFamily: 'Montserrat_600SemiBold',
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  callToAction: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.95)',
    textAlign: 'center',
    fontFamily: 'Montserrat_400Regular',
    lineHeight: 24,
    marginBottom: 40,
    paddingHorizontal: 32,
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  appSubtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    textAlign: 'center',
    fontFamily: 'Montserrat_500Medium',
    lineHeight: 24,
    marginBottom: 40,
    paddingHorizontal: 16,
    textShadowColor: 'rgba(0, 0, 0, 0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  buttonWrapper: {
    width: '85%',
  },
  gradientButton: {
    paddingVertical: 18,
    paddingHorizontal: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 60,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
      },
      android: {
        elevation: 8,
      },
      web: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
      },
    }),
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    fontFamily: 'Montserrat_600SemiBold',
    letterSpacing: 0.3,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'Montserrat_600SemiBold',
  },
  footerSection: {
    paddingBottom: 10,
  },
  footerText: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.7)',
    textAlign: 'center',
    fontFamily: 'Montserrat_400Regular',
  },
});

export default HomeScreen;
