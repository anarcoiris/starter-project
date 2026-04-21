import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// TODO: import your use case and mock repository here

class MockAuthRepository extends Mock {
  // implements AuthRepository
}

void main() {
  late MockAuthRepository mockRepo;

  setUp(() {
    mockRepo = MockAuthRepository();
  });

  group('GetAuthsUseCase', () {
    test('returns list of auths on success', () async {
      // arrange
      // when(mockRepo.getAll()).thenAnswer((_) async => [...]);
      // act
      // assert
    });
  });
}
