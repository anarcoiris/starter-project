import 'dart:io';
import 'package:dio/dio.dart';
import 'package:news_app_clean_architecture/core/constants/constants.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/local/app_database.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/models/article.dart';
import 'package:news_app_clean_architecture/core/resources/data_state.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/entities/article.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/article_repository.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/firebase_data_source.dart';

import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/news_api_service.dart';

class ArticleRepositoryImpl implements ArticleRepository {
  final NewsApiService _newsApiService;
  final FirebaseDataSource _firebaseDataSource;
  final AppDatabase _appDatabase;

  ArticleRepositoryImpl(
    this._newsApiService,
    this._firebaseDataSource,
    this._appDatabase,
  );
  
  @override
  Future<DataState<List<ArticleEntity>>> getNewsArticles() async {
   try {
     // Local API is primary
     final httpResponse = await _newsApiService.getNewsArticles(
       apiKey: newsAPIKey,
       country: countryQuery,
       category: categoryQuery,
     );

     if (httpResponse.response.statusCode == HttpStatus.ok) {
       return DataSuccess(httpResponse.data);
     } else {
       return await _getFirebaseFallback();
     }
   } catch (e) {
     return await _getFirebaseFallback();
   }
  }

  Future<DataState<List<ArticleModel>>> _getFirebaseFallback() async {
    try {
      final articles = await _firebaseDataSource.getArticles();
      return DataSuccess(articles);
    } catch (e) {
      return DataFailed(DioException(
        error: "Both Local and Firebase backends are unavailable",
        requestOptions: RequestOptions(path: 'articles')
      ));
    }
  }

  @override
  Future<DataState<void>> postArticle(ArticleEntity article) async {
    final model = ArticleModel.fromEntity(article);
    try {
      final httpResponse = await _newsApiService.postArticle(article: model);
      
      if (httpResponse.response.statusCode == HttpStatus.ok || httpResponse.response.statusCode == HttpStatus.created) {
        return DataSuccess(null);
      } else {
        throw Exception("Local API failed with status ${httpResponse.response.statusCode}");
      }
    } catch (e) {
      // Fallback to Firebase
      try {
        await _firebaseDataSource.postArticle(model);
        return DataSuccess(null);
      } catch (firebaseError) {
        return DataFailed(DioException(
          error: "Failed to post to both backends",
          requestOptions: RequestOptions(path: 'articles')
        ));
      }
    }
  }

  @override
  Future<List<ArticleEntity>> getSavedArticles() async {
    return _appDatabase.articleDAO.getArticles();
  }

  @override
  Future<void> removeArticle(ArticleEntity article) {
    return _appDatabase.articleDAO.deleteArticle(ArticleModel.fromEntity(article));
  }

  @override
  Future<void> saveArticle(ArticleEntity article) {
    return _appDatabase.articleDAO.insertArticle(ArticleModel.fromEntity(article));
  }
}