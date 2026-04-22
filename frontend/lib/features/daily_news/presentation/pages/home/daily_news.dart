import 'dart:async';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:news_app_clean_architecture/core/constants/app_colors.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/entities/article.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/widgets/article_tile.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/widgets/cta_banner.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/widgets/owl_assistant.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/widgets/assistant_brain.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/bloc/article/remote/remote_article_bloc.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/bloc/article/remote/remote_article_event.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/bloc/article/remote/remote_article_state.dart';
import 'package:news_app_clean_architecture/core/analytics/analytics_repository.dart';
import 'package:news_app_clean_architecture/injection_container.dart';

class DailyNews extends StatefulWidget {
  const DailyNews({Key? key}) : super(key: key);

  @override
  State<DailyNews> createState() => _DailyNewsState();
}

class _DailyNewsState extends State<DailyNews> {
  late ScrollController _scrollController;
  bool _isOwlVisible = true;
  Timer? _visibilityTimer;
  String _assistantMessage = 'Hola, soy tu asistente Owl. Toca aquí para analizar noticias.';

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _visibilityTimer?.cancel();
    super.dispose();
  }

  void _handleScrollNotification(ScrollNotification notification) {
    if (notification is ScrollStartNotification) {
      if (_isOwlVisible) {
        setState(() {
          _isOwlVisible = false;
        });
      }
      _visibilityTimer?.cancel();
    } else if (notification is ScrollEndNotification) {
      _visibilityTimer?.cancel();
      _visibilityTimer = Timer(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _isOwlVisible = true;
            // Update message based on visible content (simplified)
            _assistantMessage = AssistantBrain.getRandomMessage();
          });
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppbar(context),
      body: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          _handleScrollNotification(notification);
          return false;
        },
        child: _buildBody(context),
      ),
      bottomNavigationBar: _buildBottomNav(context),
    );
  }

  PreferredSizeWidget _buildAppbar(BuildContext context) {
    return AppBar(
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.15),
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.primary, width: 1.5),
            ),
            child: const Text('🦉', style: TextStyle(fontSize: 18)),
          ),
          const SizedBox(width: 10),
          RichText(
            text: const TextSpan(
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white, letterSpacing: 0.5),
              children: [
                TextSpan(text: 'Symmetry'),
                TextSpan(text: ' News', style: TextStyle(color: AppColors.primary)),
              ],
            ),
          ),
        ],
      ),
      actions: [
        IconButton(
          onPressed: () {},
          icon: const Icon(Icons.search, color: AppColors.primary),
        ),
        const SizedBox(width: 8),
      ],
    );
  }

  Widget _buildBody(BuildContext context) {
    return BlocBuilder<RemoteArticlesBloc, RemoteArticlesState>(
      builder: (_, state) {
        if (state is RemoteArticlesLoading) {
          return const Center(child: CupertinoActivityIndicator(color: AppColors.primary));
        }
        if (state is RemoteArticlesError) {
          return Center(
            child: IconButton(
              onPressed: () => _onRefresh(context),
              icon: const Icon(Icons.refresh, color: AppColors.primary),
            ),
          );
        }
        if (state is RemoteArticlesDone) {
          return Stack(
            children: [
              RefreshIndicator(
                onRefresh: () => _onRefresh(context),
                color: AppColors.primary,
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.only(bottom: 100),
                  itemCount: (state.articles?.length ?? 0) + 1,
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      return const CtaBanner();
                    }
                    final article = state.articles![index - 1];
                    return ArticleWidget(
                      article: article,
                      onArticlePressed: (article) => _onArticlePressed(context, article),
                    );
                  },
                ),
              ),
              Positioned(
                bottom: 20,
                right: 0,
                child: OwlAssistant(
                  text: _assistantMessage,
                  isVisible: _isOwlVisible,
                ),
              ),
            ],
          );
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildBottomNav(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.background,
        border: Border(top: BorderSide(color: AppColors.primary.withValues(alpha: 0.1), width: 1)),
      ),
      child: BottomNavigationBar(
        onTap: (index) {
          if (index == 2) _onPublishPressed(context);
          if (index == 3) _onShowSavedArticlesViewTapped(context);
        },
        currentIndex: 0,
        backgroundColor: AppColors.background,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textMuted,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.grid_view_rounded), label: 'Feed'),
          BottomNavigationBarItem(icon: Icon(Icons.trending_up), label: 'Tópicos'),
          BottomNavigationBarItem(
            icon: CircleAvatar(
              radius: 18,
              backgroundColor: AppColors.primary,
              child: Icon(Icons.add, color: Colors.black),
            ),
            label: 'Publicar',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.bookmark_border), label: 'Guardado'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'Perfil'),
        ],
      ),
    );
  }

  void _onArticlePressed(BuildContext context, ArticleEntity article) {
    sl<AnalyticsRepository>().trackArticleView(article);
    Navigator.pushNamed(context, '/ArticleDetails', arguments: article);
  }

  void _onShowSavedArticlesViewTapped(BuildContext context) {
    Navigator.pushNamed(context, '/SavedArticles');
  }

  void _onPublishPressed(BuildContext context) {
    Navigator.pushNamed(context, '/PublishArticle');
  }

  Future<void> _onRefresh(BuildContext context) async {
    context.read<RemoteArticlesBloc>().add(const GetArticles());
  }
}
