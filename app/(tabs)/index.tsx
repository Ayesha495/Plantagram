import { View, StyleSheet } from 'react-native';

import { ThemedText } from '@/components/themed-text';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <ThemedText type="title">Plantagram app is working</ThemedText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
