import 'dart:developer' as developer;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:get_it/get_it.dart';
import 'package:dio/dio.dart';
import 'package:floor/floor.dart';

import 'package:news_app_clean_architecture/core/core.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/local/app_database.dart';

Future<void> initCoreDependencies(GetIt sl) async {
  // Floor Database
  final migration1to2 = Migration(1, 2, (database) async {
    await database.execute('DROP TABLE IF EXISTS article');
    await database.execute('CREATE TABLE IF NOT EXISTS `article` (`articleId` TEXT NOT NULL, `author` TEXT, `title` TEXT, `description` TEXT, `url` TEXT, `urlToImage` TEXT, `publishedAt` TEXT, `content` TEXT, `tokensEarned` REAL, PRIMARY KEY (`articleId`))');
  });

  final database = await $FloorAppDatabase
      .databaseBuilder('app_database.db')
      .addMigrations([migration1to2])
      .build();

  sl.registerSingleton<AppDatabase>(database);
  
  // Firebase
  sl.registerSingleton<FirebaseFirestore>(FirebaseFirestore.instance);
  sl.registerSingleton<FirebaseAuth>(FirebaseAuth.instance);
  sl.registerSingleton<FirebaseStorage>(FirebaseStorage.instance);

  // Dio (Local Backend / FastAPI)
  final backendDio = Dio(
    BaseOptions(
      baseUrl: ApiConfig.backendBaseUrl,
      connectTimeout: const Duration(milliseconds: 5000),
      receiveTimeout: const Duration(milliseconds: 5000),
    ),
  );
  
  backendDio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) {
      developer.log('DIO REQUEST[${options.method}] => PATH: ${options.path}', name: 'SymmetryNet');
      return handler.next(options);
    },
    onResponse: (response, handler) {
      developer.log('DIO RESPONSE[${response.statusCode}] => PATH: ${response.requestOptions.path}', name: 'SymmetryNet');
      return handler.next(response);
    },
    onError: (DioException e, handler) {
      developer.log('DIO ERROR[${e.response?.statusCode}] => PATH: ${e.requestOptions.path}', name: 'SymmetryNet', error: e);
      return handler.next(e);
    },
  ));

  sl.registerSingleton<Dio>(backendDio, instanceName: 'backend');
}
