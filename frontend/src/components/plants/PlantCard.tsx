import React from 'react';
import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';
import { Plant } from '../../types/plant';

interface PlantCardProps {
  plant: Plant;
  onPress: (plant: Plant) => void;
  language?: 'en' | 'ur';
}

export default function PlantCard({ plant, onPress, language = 'en' }: PlantCardProps) {
  const displayName = language === 'ur' ? plant.name_urdu : plant.name;
  
  const getCareColor = (level: string) => {
    switch (level) {
      case 'Easy': return '#4ade80';
      case 'Medium': return '#fbbf24';
      case 'Hard': return '#f87171';
      default: return '#9ca3af';
    }
  };

  return (
    <TouchableOpacity 
      style={styles.card} 
      onPress={() => onPress(plant)}
      activeOpacity={0.7}
    >
      {/* Plant Image */}
      <Image
        source={{ uri: plant.image_url || 'https://via.placeholder.com/150' }}
        style={styles.image}
        resizeMode="cover"
      />
      
      {/* Plant Info */}
      <View style={styles.info}>
        <Text style={styles.name} numberOfLines={2}>
          {displayName}
        </Text>
        
        {plant.scientific_name && (
          <Text style={styles.scientific} numberOfLines={1}>
            {plant.scientific_name}
          </Text>
        )}
        
        <View style={styles.badges}>
          {/* Category Badge */}
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{plant.category}</Text>
          </View>
          
          {/* Care Level Badge */}
          <View style={[styles.careBadge, { backgroundColor: getCareColor(plant.care_level) }]}>
            <Text style={styles.careText}>{plant.care_level}</Text>
          </View>
        </View>
        
        {/* Beginner Friendly Tag */}
        {plant.is_beginner_friendly && (
          <View style={styles.beginnerTag}>
            <Text style={styles.beginnerText}>🌱 Beginner Friendly</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 200,
    backgroundColor: '#f3f4f6',
  },
  info: {
    padding: 12,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  scientific: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#6b7280',
    marginBottom: 8,
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  categoryBadge: {
    backgroundColor: '#dbeafe',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  categoryText: {
    fontSize: 12,
    color: '#1e40af',
    fontWeight: '500',
  },
  careBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  careText: {
    fontSize: 12,
    color: 'white',
    fontWeight: '600',
  },
  beginnerTag: {
    backgroundColor: '#d1fae5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  beginnerText: {
    fontSize: 12,
    color: '#065f46',
    fontWeight: '500',
  },
});