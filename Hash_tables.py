import unittest
import math

class HashTable:
    """
    Реализация хеш-таблицы с методом цепочек для разрешения коллизий
    и автоматическим рехешированием при достижении порога заполнения.
    """
    
    def __init__(self, initial_size=8, load_factor=0.75):
        """
        Инициализация хеш-таблицы.
        
        Параметры:
            initial_size (int): Начальный размер таблицы (должен быть степенью двойки)
            load_factor (float): Коэффициент заполнения (0.75 по умолчанию)
        """
        if not self._is_power_of_two(initial_size):
            raise ValueError("Размер таблицы должен быть степенью двойки")
            
        self.size = initial_size
        self.load_factor = load_factor
        self.threshold = int(self.size * self.load_factor)
        self.count = 0
        self.table = [[] for _ in range(self.size)]
    
    def _is_power_of_two(self, n):
        """Проверяет, является ли число степенью двойки."""
        return (n & (n - 1)) == 0 and n != 0
    
    def _hash(self, key):
        """
        Внутренняя хеш-функция, преобразующая ключ в индекс таблицы.
        Использует встроенную функцию hash() и модуль от размера таблицы.
        """
        return hash(key) % self.size
    
    def _resize(self, new_size):
        """
        Изменяет размер таблицы и перехеширует все существующие элементы.
        
        Параметры:
            new_size (int): Новый размер таблицы (должен быть степенью двойки)
        """
        if not self._is_power_of_two(new_size):
            raise ValueError("Новый размер таблицы должен быть степенью двойки")
        
        old_table = self.table
        self.size = new_size
        self.threshold = int(self.size * self.load_factor)
        self.table = [[] for _ in range(self.size)]
        self.count = 0
        
        # Перехеширование всех элементов
        for bucket in old_table:
            for key, value in bucket:
                self.put(key, value)
    
    def put(self, key, value):
        """
        Добавляет пару ключ-значение в таблицу или обновляет значение,
        если ключ уже существует.
        
        Параметры:
            key: Ключ для вставки (должен быть хешируемым)
            value: Значение, ассоциированное с ключом
        """
        # Проверяем, нужно ли увеличить таблицу
        if self.count >= self.threshold:
            self._resize(self.size * 2)
        
        index = self._hash(key)
        bucket = self.table[index]
        
        # Проверяем, есть ли уже такой ключ в цепочке
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # Обновляем значение
                return
        
        # Если ключ не найден, добавляем новую пару
        bucket.append((key, value))
        self.count += 1
    
    def get(self, key, default=None):
        """
        Получает значение по ключу.
        
        Параметры:
            key: Ключ для поиска
            default: Значение, возвращаемое если ключ не найден
            
        Возвращает:
            Значение, ассоциированное с ключом, или default
        """
        index = self._hash(key)
        bucket = self.table[index]
        
        for k, v in bucket:
            if k == key:
                return v
                
        return default
    
    def delete(self, key):
        """
        Удаляет пару ключ-значение из таблицы.
        
        Параметры:
            key: Ключ для удаления
            
        Возвращает:
            Удаленное значение или None, если ключ не найден
        """
        index = self._hash(key)
        bucket = self.table[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.count -= 1
                
                # Проверяем, нужно ли уменьшить таблицу
                if self.size > 8 and self.count < self.threshold // 4:
                    self._resize(max(8, self.size // 2))
                
                return v
                
        return None
    
    def __contains__(self, key):
        """Проверяет наличие ключа в таблице."""
        return self.get(key) is not None
    
    def __len__(self):
        """Возвращает количество элементов в таблице."""
        return self.count
    
    def items(self):
        """Генератор всех пар ключ-значение в таблице."""
        for bucket in self.table:
            for key, value in bucket:
                yield (key, value)
    
    def keys(self):
        """Генератор всех ключей в таблице."""
        for key, _ in self.items():
            yield key
    
    def values(self):
        """Генератор всех значений в таблице."""
        for _, value in self.items():
            yield value

class TestHashTable(unittest.TestCase):
    """Тесты для реализации хеш-таблицы."""
    
    def setUp(self):
        self.ht = HashTable()
    
    def test_put_and_get(self):
        """Тестирование базовой вставки и получения."""
        self.ht.put("name", "Alice")
        self.ht.put("age", 30)
        self.ht.put(42, "The Answer")
        
        self.assertEqual(self.ht.get("name"), "Alice")
        self.assertEqual(self.ht.get("age"), 30)
        self.assertEqual(self.ht.get(42), "The Answer")
        self.assertIsNone(self.ht.get("nonexistent"))
    
    def test_update(self):
        """Тестирование обновления значения."""
        self.ht.put("key", "value1")
        self.assertEqual(self.ht.get("key"), "value1")
        
        self.ht.put("key", "value2")
        self.assertEqual(self.ht.get("key"), "value2")
    
    def test_delete(self):
        """Тестирование удаления."""
        self.ht.put("key", "value")
        self.assertEqual(self.ht.get("key"), "value")
        
        deleted = self.ht.delete("key")
        self.assertEqual(deleted, "value")
        self.assertIsNone(self.ht.get("key"))
    
    def test_collisions(self):
        """Тестирование обработки коллизий."""
        # Создаем маленькую таблицу для увеличения вероятности коллизий
        small_ht = HashTable(initial_size=4)
        
        # Добавляем несколько ключей, которые могут попасть в одну ячейку
        small_ht.put("a", 1)
        small_ht.put("e", 2)  # Может быть коллизия с "a"
        small_ht.put("i", 3)  # Может быть коллизия с предыдущими
        
        self.assertEqual(small_ht.get("a"), 1)
        self.assertEqual(small_ht.get("e"), 2)
        self.assertEqual(small_ht.get("i"), 3)
    
    def test_resize(self):
        """Тестирование автоматического изменения размера."""
        # Начальный размер 8, порог заполнения 6 (8 * 0.75)
        self.assertEqual(self.ht.size, 8)
        
        # Добавляем 6 элементов - до порога
        for i in range(6):
            self.ht.put(f"key{i}", i)
        
        self.assertEqual(self.ht.size, 8)  # Размер не должен измениться
        
        # Добавляем еще один элемент - должно вызвать увеличение
        self.ht.put("key6", 6)
        self.assertEqual(self.ht.size, 16)  # Размер удвоился
        
        # Удаляем элементы - должно вызвать уменьшение
        for i in range(5):
            self.ht.delete(f"key{i}")
        
        self.assertEqual(self.ht.size, 8)  # Размер уменьшился
    
    def test_iterators(self):
        """Тестирование итераторов."""
        data = {"a": 1, "b": 2, "c": 3}
        for k, v in data.items():
            self.ht.put(k, v)
        
        # Проверяем items()
        self.assertSetEqual(set(self.ht.items()), set(data.items()))
        
        # Проверяем keys()
        self.assertSetEqual(set(self.ht.keys()), set(data.keys()))
        
        # Проверяем values()
        self.assertSetEqual(set(self.ht.values()), set(data.values()))

if __name__ == "__main__":
    unittest.main()
