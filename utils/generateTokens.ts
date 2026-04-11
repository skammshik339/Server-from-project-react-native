import jwt from "jsonwebtoken";

export default class TokenUtils {
  static generateAccessToken(payload: string) {
    return jwt.sign({ userId: payload }, process.env.JWT_ACCESS_SECRET!, { expiresIn: "15m" });
  }
  
  static generateRefreshToken(payload: string) {
    return jwt.sign({ userId: payload }, process.env.JWT_REFRESH_SECRET!, {
      expiresIn: "7d",
    });
  }
  
  static verifyAccessToken(token: string) {
    return jwt.verify(token, process.env.JWT_ACCESS_SECRET!);
  }
  
  static verifyAccessRefresh(token: string) {
    return jwt.verify(token, process.env.JWT_REFRESH_SECRET!);
  }
  
  static generateDuoTokens(payload: string) {
    return {
      accessToken: this.generateAccessToken(payload),
      refreshToken: this.generateRefreshToken(payload),
    };
  }
}