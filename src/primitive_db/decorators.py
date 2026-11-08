import functools
import time
from typing import Any, Callable


def handle_db_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор для централизованной обработки ошибок СУБД."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база пуста.")
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.", flush=True)
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}", flush=True)
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None
    return wrapper


def confirm_action(action_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:  # noqa: E501
    """Декоратор с аргументом для подтверждения опасных операций."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            choice = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower() # noqa: E501
            if choice == "y":
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return None
        return wrapper
    return decorator


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор для замера времени выполнения функций."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция <{func.__name__}> выполнилась за {execution_time:.3f} секунд.")
        return result
    return wrapper


def create_cacher() -> Callable[..., Any]:
    """Функция с замыканием для кэширования результатов select с поддержкой очистки."""
    cache: dict[str, Any] = {}

    def cache_result(key: str, value_func: Callable[[], Any] = None, clear_cache: bool = False) -> Any:  # noqa: E501
        if clear_cache:
            cache.clear()
            return None
            
        if key in cache:
            return cache[key]
        
        if value_func is not None:
            result = value_func()
            if result is not None:
                cache[key] = result
            return result
        return None

    return cache_result