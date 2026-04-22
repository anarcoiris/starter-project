import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:news_app_clean_architecture/core/constants/app_colors.dart';

class TopicsPage extends StatelessWidget {
  const TopicsPage({super.key});

  final List<Map<String, dynamic>> topics = const [
    {'name': 'AI & ROBOTICS', 'icon': Icons.psychology, 'count': 24},
    {'name': 'CYBER SECURITY', 'icon': Icons.security, 'count': 18},
    {'name': 'GEOPOLITICS', 'icon': Icons.public, 'count': 42},
    {'name': 'FINANCIAL MARKETS', 'icon': Icons.trending_up, 'count': 31},
    {'name': 'SPACE TECH', 'icon': Icons.rocket_launch, 'count': 12},
    {'name': 'BIOTECH', 'icon': Icons.science, 'count': 9},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF03050F),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('NODOS DE INTERÉS', style: TextStyle(letterSpacing: 3, fontWeight: FontWeight.bold)),
      ),
      body: Stack(
        children: [
          // Background Glow effect
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.cyanAccent.withOpacity(0.05),
              ),
            ),
          ),
          
          GridView.builder(
            padding: const EdgeInsets.all(20),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 0.85,
            ),
            itemCount: topics.length,
            itemBuilder: (context, index) {
              return _buildTopicCard(context, topics[index]);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTopicCard(BuildContext context, Map<String, dynamic> topic) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.03),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.05)),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withOpacity(0.05),
                Colors.white.withOpacity(0.01),
              ],
            ),
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () {
                // Implement filter logic or just show a coming soon toast
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Filtrando por ${topic['name']}...'),
                    backgroundColor: Colors.cyanAccent.withOpacity(0.1),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.cyanAccent.withOpacity(0.1),
                      ),
                      child: Icon(topic['icon'], color: Colors.cyanAccent, size: 30),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      topic['name'],
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${topic['count']} ALERTAS',
                        style: const TextStyle(color: Colors.cyanAccent, fontSize: 8, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
