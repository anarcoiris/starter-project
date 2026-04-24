import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:news_app_clean_architecture/core/core.dart';
import 'package:news_app_clean_architecture/features/auth/presentation/bloc/auth_cubit.dart';
import 'package:news_app_clean_architecture/core/constants/app_colors.dart';
import 'package:news_app_clean_architecture/core/constants/constants.dart';

import 'package:news_app_clean_architecture/features/daily_news/domain/daily_news_domain.dart';
import 'package:news_app_clean_architecture/injection_container.dart';

class ProfilePage extends StatefulWidget {
  final String? userId;
  const ProfilePage({super.key, this.userId});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final TextEditingController _bioController = TextEditingController();
  bool _isEditing = false;
  double _balance = 0.0;
  UserEntity? _publicUser;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    if (widget.userId != null) {
      _fetchPublicProfile();
    } else {
      _fetchBalance();
    }
  }

  void _fetchPublicProfile() async {
    setState(() => _isLoading = true);
    final result = await sl<GetPublicProfileUseCase>().call(params: widget.userId);
    if (mounted && result is DataSuccess) {
      setState(() {
        _publicUser = result.data;
        _isLoading = false;
      });
    }
  }

  void _fetchBalance() async {
    try {
      final authState = context.read<AuthCubit>().state;
      if (authState is! Authenticated) return;

      final result = await sl<GetBalanceUseCase>().call(params: authState.user.uid);
      if (mounted && result is DataSuccess) {
        setState(() {
          _balance = result.data!;
        });
      }
    } catch (e) {
      debugPrint('Error fetching balance: $e');
    }
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
        child: AlertDialog(
          backgroundColor: const Color(0xFF0A0C1A),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: const BorderSide(color: Colors.redAccent, width: 1),
          ),
          title: const Text(
            'DESCONEXIÓN DE AGENTE',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, letterSpacing: 1),
          ),
          content: const Text(
            '¿Está seguro de que desea finalizar su sesión en el sistema Symmetry?',
            style: TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('CANCELAR', style: TextStyle(color: Colors.white54)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                context.read<AuthCubit>().logout();
                Navigator.of(context).pushNamedAndRemoveUntil('/Login', (route) => false);
              },
              child: const Text('CONFIRMAR'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = context.watch<AuthCubit>().state;
    if (authState is! Authenticated && widget.userId == null) return const SizedBox();

    final currentUser = authState is Authenticated ? authState.user : null;
    final bool isOwnProfile = widget.userId == null || widget.userId == currentUser?.uid;
    final user = isOwnProfile ? currentUser! : _publicUser;

    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF03050F),
        body: Center(child: CircularProgressIndicator(color: AppColors.primary)),
      );
    }

    if (user == null) {
      return Scaffold(
        backgroundColor: const Color(0xFF03050F),
        appBar: AppBar(backgroundColor: Colors.transparent, elevation: 0),
        body: const Center(child: Text('AGENTE NO ENCONTRADO', style: TextStyle(color: Colors.white54))),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF03050F),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(isOwnProfile ? 'MI PERFIL DE AGENTE' : 'PERFIL DE AGENTE', style: const TextStyle(letterSpacing: 2, fontWeight: FontWeight.bold)),
        actions: [
          if (isOwnProfile)
            IconButton(
              icon: const Icon(Icons.logout, color: Colors.redAccent),
              onPressed: () => _showLogoutDialog(context),
            )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Profile Header
            Center(
              child: Stack(
                children: [
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.cyanAccent, width: 2),
                      boxShadow: [
                        BoxShadow(color: Colors.cyanAccent.withOpacity(0.2), blurRadius: 20, spreadRadius: 5)
                      ],
                    ),
                    child: CircleAvatar(
                      radius: 58,
                      backgroundColor: Colors.black,
                      backgroundImage: user.photoUrl != null ? NetworkImage(user.photoUrl!) : null,
                      child: user.photoUrl == null ? const Icon(Icons.person, size: 60, color: Colors.white24) : null,
                    ),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(color: Colors.cyanAccent, shape: BoxShape.circle),
                      child: const Icon(Icons.verified, color: Colors.black, size: 20),
                    ),
                  )
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              user.displayName?.toUpperCase() ?? 'AGENTE DESCONOCIDO',
              style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900, letterSpacing: 2),
            ),
            Text(
              user.email ?? '',
              style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, letterSpacing: 1),
            ),
            
            const SizedBox(height: 40),
            
            // Bio Section
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.03),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.white.withOpacity(0.05)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('HISTORIA DEL AGENTE (BIO)', style: TextStyle(color: Colors.white54, fontSize: 10, letterSpacing: 1)),
                      if (isOwnProfile)
                        IconButton(
                          icon: Icon(_isEditing ? Icons.check : Icons.edit, color: Colors.cyanAccent, size: 16),
                          onPressed: () {
                            if (_isEditing) {
                              context.read<AuthCubit>().updateBio(_bioController.text);
                            } else {
                              _bioController.text = user.bio ?? '';
                            }
                            setState(() => _isEditing = !_isEditing);
                          },
                        )
                    ],
                  ),
                  const SizedBox(height: 10),
                  _isEditing 
                    ? TextField(
                        controller: _bioController,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                        maxLines: 3,
                        decoration: InputDecoration(
                          filled: true,
                          fillColor: Colors.white.withOpacity(0.05),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                        ),
                      )
                    : Text(
                        user.bio ?? 'Sin biografía registrada.',
                        style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
                      ),

                ],
              ),
            ),
            
            const SizedBox(height: 40),
            
            // Stats Row
            Row(
              children: [
                _buildStatCard('REPUTACIÓN', '${user.reputationScore}', Icons.shield_outlined),
                if (isOwnProfile) ...[
                  const SizedBox(width: 12),
                  _buildStatCard('BOLSA SYM', '${_balance.toInt()}', Icons.account_balance_wallet_outlined, isHighlight: true),
                ],
                const SizedBox(width: 12),
                _buildStatCard('ARTÍCULOS', '0', Icons.article_outlined),
              ],
            ),
            
            if (!isOwnProfile) ...[
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: () {
                    developer.log('Iniciando comunicación con: ${user.uid}', name: 'SymmetrySocial');
                    Navigator.pushNamed(context, '/ChatRoom', arguments: {
                      'receiverId': user.uid,
                      'receiverName': user.displayName,
                    });
                  },
                  icon: const Icon(Icons.chat_bubble_outline),
                  label: const Text('ESTABLECER COMUNICACIÓN (CHAT)', style: TextStyle(letterSpacing: 1.5, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 10,
                    shadowColor: AppColors.primary.withOpacity(0.5),
                  ),
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, {bool isHighlight = false}) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 10),
        decoration: BoxDecoration(
          color: isHighlight ? AppColors.primary.withOpacity(0.05) : Colors.white.withOpacity(0.03),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isHighlight ? AppColors.primary.withOpacity(0.2) : Colors.white.withOpacity(0.05)),
        ),
        child: Column(
          children: [
            Icon(icon, color: isHighlight ? AppColors.primary : Colors.cyanAccent, size: 24),
            const SizedBox(height: 12),
            Text(value, style: TextStyle(color: isHighlight ? AppColors.primary : Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            Text(label, style: const TextStyle(color: Colors.white54, fontSize: 8, letterSpacing: 1), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}
