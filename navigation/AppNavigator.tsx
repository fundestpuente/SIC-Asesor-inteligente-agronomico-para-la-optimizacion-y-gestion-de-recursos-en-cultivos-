import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Crop } from '../constants/crops';

import SplashScreen from '../screens/SplashScreen';
import WelcomeScreen from '../screens/WelcomeScreen';
import HomeScreen from '../screens/HomeScreen';
import CropSelectionScreen from '../screens/CropSelectionScreen';
import DataInputScreen from '../screens/DataInputScreen';
import ResultScreen from '../screens/ResultScreen';

export type RootStackParamList = {
  Splash: undefined;
  Welcome: undefined;
  Home: undefined;
  CropSelection: undefined;
  DataInput: { crop: Crop };
  Result: {
    crop: Crop;
    cropName: string;
    ph: number;
    latitude: number;
    longitude: number;
    nutrientes: {
      N: number;
      P: number;
      K: number;
    };
    clima: {
      temperature: number;
      humidity: number;
      rainfall: number;
    };
    recomendacion: string;
  };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Splash"
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="Splash" component={SplashScreen} />
        <Stack.Screen name="Welcome" component={WelcomeScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="CropSelection" component={CropSelectionScreen} />
        <Stack.Screen name="DataInput" component={DataInputScreen} />
        <Stack.Screen name="Result" component={ResultScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
