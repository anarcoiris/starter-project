import 'package:dio/dio.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/models/article.dart';
import 'package:retrofit/retrofit.dart';

class NewsApiService {
  final Dio _dio;

  NewsApiService(this._dio);

  Future<HttpResponse<List<ArticleModel>>> getNewsArticles({
    String? apiKey,
    String? country,
    String? category,
  }) async {
    try {
      final response = await _dio.get(
        'articles/',
        queryParameters: {
          'category': category,
          'limit': 20,
        },
      );


      final List<dynamic> data = response.data is List
          ? response.data
          : (response.data is Map ? (response.data['articles'] ?? []) : []);

      final List<ArticleModel> articles =
          data.map((e) => ArticleModel.fromJson(e)).toList();

      return HttpResponse(articles, response);
    } catch (e) {
      rethrow;
    }
  }

  Future<HttpResponse<void>> postArticle({
    ArticleModel? article,
  }) async {
    try {
      final response = await _dio.post(
        'articles/',
        data: article?.toJson(),
      );

      return HttpResponse(null, response);
    } catch (e) {
      rethrow;
    }
  }

  Future<HttpResponse<Map<String, dynamic>>> voteArticle(String articleId, String userId, String vote) async {
    try {
      final response = await _dio.post(
        'articles/$articleId/vote',
        data: {
          'userId': userId,
          'vote': vote,
        },
      );
      return HttpResponse(response.data as Map<String, dynamic>, response);
    } catch (e) {
      rethrow;
    }
  }

  Future<HttpResponse<Map<String, dynamic>>> generateDailyNewspaper() async {
    try {
      final response = await _dio.post('articles/generate-daily');
      return HttpResponse(response.data as Map<String, dynamic>, response);
    } catch (e) {
      rethrow;
    }
  }
}