import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { Link, router } from 'expo-router';
import { authService } from '../../src/services/AuthService';

export default function SignupScreen() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    // Validation
    if (!username || !email || !password || !password2) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password !== password2) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await authService.signup({
        username,
        email,
        password,
        password2,
      });
      
      Alert.alert(
        'Success', 
        `Welcome to Plantagram, ${response.user.username}!`,
        [
          {
            text: 'OK',
            onPress: () => router.replace('../(tabs)'),
          }
        ]
      );
    } catch (error: any) {
      console.error('Signup failed:', error);
      
      // Handle specific error messages from backend
      let errorMessage = 'Signup failed. Please try again.';
      
      if (error.email) {
        errorMessage = error.email[0] || 'Email is invalid';
      } else if (error.username) {
        errorMessage = error.username[0] || 'Username is already taken';
      } else if (error.password) {
        errorMessage = error.password[0] || 'Password is too weak';
      } else if (error.error) {
        errorMessage = error.error;
      }
      
      Alert.alert('Signup Failed', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.logo}>🌱</Text>
      <Text style={styles.title}>Create Account</Text>
      <Text style={styles.subtitle}>Join Plantagram</Text>

      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor="#999"
        autoCapitalize="none"
        value={username}
        onChangeText={setUsername}
        editable={!loading}
      />

      <TextInput
        style={styles.input}
        placeholder="Email"
        placeholderTextColor="#999"
        keyboardType="email-address"
        autoCapitalize="none"
        value={email}
        onChangeText={setEmail}
        editable={!loading}
      />

      <TextInput
        style={styles.input}
        placeholder="Password (min 8 characters)"
        placeholderTextColor="#999"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        editable={!loading}
      />

      <TextInput
        style={styles.input}
        placeholder="Confirm Password"
        placeholderTextColor="#999"
        secureTextEntry
        value={password2}
        onChangeText={setPassword2}
        editable={!loading}
      />

      <TouchableOpacity 
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleSignup}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.buttonText}>Sign Up</Text>
        )}
      </TouchableOpacity>

      <Link href="/(auth)/login" style={styles.link}>
        <Text style={styles.linkText}>Already have an account? Login</Text>
      </Link>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  logo: {
    fontSize: 80,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2d6a4f',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 40,
  },
  input: {
    width: '100%',
    height: 50,
    backgroundColor: 'white',
    borderRadius: 10,
    paddingHorizontal: 15,
    marginBottom: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  button: {
    width: '100%',
    height: 50,
    backgroundColor: '#2d6a4f',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
  },
  buttonDisabled: {
    backgroundColor: '#95b8a7',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  link: {
    marginTop: 20,
  },
  linkText: {
    color: '#2d6a4f',
    fontSize: 14,
  },
});