import { Request, Response } from "express";
import authService from "../services/authServices";
import User from '../models/User'

export const register = async (req: Request, res: Response) => {
  try {
    const { email, password, name } = req.body;
    if (!email || !password || !name) {
      return res.status(400).json({ message: "Все поля обязательны" });
    }
    const result = await authService.register(name, email, password);
    res.status(201).json({
      message: result.message,
      user: result.user,
    });
  } catch (error: any) {
    if (error.message === "пользователь уже существует") {
      return res
        .status(400)
        .json({ message: "Пользователь с таким email уже существует" });
    }
    res.status(500).json({ message: "Server error", error: error.message });
  }
};


export const verifyEmail = async (req: Request, res: Response) => {
  try {
    const { token } = req.query;
    if (!token) return res.send("<h1>Ошибка: нет токена</h1>");
    
    const result = await authService.verifyEmail(token as string);
    res.send(`<h1>Email подтвержден!</h1><script>setTimeout(() => location.href='yourapp://login', 2000);</script>`);
  } catch (error: any) {
    res.send(`<h1>Ошибка: ${error.message}</h1>`);
  }
};

export const login = async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({
        message: "Email и пароль обязательны",
      });
    }

    const result = await authService.login(email, password);
    res.json({
      message: "Login successful",
      user: result.user,
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
    });
  } catch (error: any) {
    if (error.message === "Пользователя с таким email не существует") {
      return res.status(401).json({
        message: "Пользователя с таким email не существует",
      });
    }
    if (error.message === "Неправильный пароль") {
      return res.status(401).json({
        message: "Неправильный пароль!",
      });
    }
     if (error.message === "Email не подтвержден") {
      return res.status(401).json({ message: "Email не подтвержден. Проверьте почту" });
    }
    res.status(500).json({
      message: "Server error",
      error: error.message,
    });
  }
};

export const logout = async (req: any, res: Response) => {
  try {
    const userId = req.user?._id?.toString();

    if (!userId) {
      return res.status(401).json({ message: "Пользователь не авторизован" });
    }

    const result = await authService.logout(userId);
    res.json(result);
  } catch (error: any) {
    if (error.message === "Пользователь не найден") {
      return res.status(404).json({ message: "Пользователь не найден" });
    }

    res.status(500).json({
      message: "Server error",
      error: error.message,
    });
  }
};

export const getMe = async (req: any, res: Response) => {
  res.json({ user: req.user });
};

export const refreshToken = async (req: Request, res: Response) => {
  try {
    const refreshToken = req.header("X-Refresh-Token");

    if (!refreshToken) {
      return res.status(400).json({
        message: "Refresh токен не предоставлен",
      });
    }

    const result = await authService.refreshToken(refreshToken);

    res.json({
      message: "Токены успешно обновлены",
      ...result,
    });
  } catch (error: any) {
    switch (error.message) {
      case "Refresh токен истёк":
        return res.status(401).json({
          message: "Refresh токен истёк. Войдите снова.",
        });

      case "Недействительный refresh токен":
        return res.status(401).json({
          message: "Недействительный refresh токен. Войдите снова.",
        });

      case "Подозрительный refresh токен":
        return res.status(401).json({
          message: "Принудительный выход, попытка взлома",
        });

      case "Пользователь не найден":
        return res.status(404).json({
          message: "Пользователь не найден",
        });

      case "Нету refresh токена":
        return res.status(400).json({
          message: "Refresh токен не предоставлен",
        });

      default:
        console.error("Ошибка refreshToken:", error);
        return res.status(500).json({
          message: "Ошибка сервера",
        });
    }
  }
};

export const checkVerificationStatus = async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    const user = await User.findById(userId).select('isEmailVerified');
    res.json({ isEmailVerified: user?.isEmailVerified || false });
  } catch (error) {
    res.json({ isEmailVerified: false });
  }
};
