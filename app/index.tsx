import { Redirect } from 'expo-router';

export default function Index() {
  // Redirect to login screen
  return <Redirect href="/(auth)/login" />;
}