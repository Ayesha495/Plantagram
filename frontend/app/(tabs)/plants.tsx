import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, TextInput, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';
import { plantService } from '../../src/services/plantService';
import { Plant } from '../../src/types/plant';
import PlantCard from '../../src/components/plants/PlantCard';
import { storage } from '../../src/services/storage';

export default function PlantsScreen() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [language, setLanguage] = useState<'en' | 'ur'>('en');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserLanguage();
    loadPlants();
  }, []);

  const loadUserLanguage = async () => {
    const user = await storage.getUser();
    if (user && user.language_preference) {
      setLanguage(user.language_preference);
    }
  };

  const loadPlants = async () => {
    try {
      setLoading(true);
      const response = await plantService.getPlants(1, 30);
      setPlants(response.results);
      setHasMore(response.next !== null);
      setPage(1);
    } catch (error) {
      console.error('Load plants error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMorePlants = async () => {
    if (!hasMore || loading) return;

    try {
      const nextPage = page + 1;
      const response = await plantService.getPlants(nextPage, 30);
      setPlants([...plants, ...response.results]);
      setHasMore(response.next !== null);
      setPage(nextPage);
    } catch (error) {
      console.error('Load more error:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadPlants();
      return;
    }

    try {
      setLoading(true);
      const response = await plantService.searchPlants(searchQuery);
      setPlants(response.results);
      setHasMore(response.next !== null);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPlants();
    setRefreshing(false);
  };

  const handlePlantPress = (plant: Plant) => {
    router.push(`/plant/${plant.id}`);
  };

  if (loading && plants.length === 0) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2d6a4f" />
        <Text style={styles.loadingText}>Loading plants...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🌱 Plant Database</Text>
        <Text style={styles.subtitle}>{plants.length} plants available</Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder={language === 'ur' ? 'پودے تلاش کریں...' : 'Search plants...'}
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>🔍</Text>
        </TouchableOpacity>
      </View>

      {/* Plant List */}
      <FlatList
        data={plants}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <PlantCard plant={item} onPress={handlePlantPress} language={language} />
        )}
        onEndReached={loadMorePlants}
        onEndReachedThreshold={0.5}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No plants found</Text>
          </View>
        }
        ListFooterComponent={
          hasMore && plants.length > 0 ? (
            <View style={styles.footer}>
              <ActivityIndicator size="small" color="#2d6a4f" />
            </View>
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    color: '#6b7280',
    fontSize: 16,
  },
  header: {
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    height: 48,
    backgroundColor: 'white',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  searchButton: {
    width: 48,
    height: 48,
    backgroundColor: '#2d6a4f',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    fontSize: 20,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#9ca3af',
  },
  footer: {
    padding: 16,
    alignItems: 'center',
  },
});
