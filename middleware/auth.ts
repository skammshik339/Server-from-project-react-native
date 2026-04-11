import jwt from 'jsonwebtoken';
import User from '../models/User';
import TokenUtils from '../utils/generateTokens';

export const authMiddleware = async (req: any, res: any, next: any) => {
  try {
    const accessToken = req.header('Authorization')?.replace('Bearer ', '');

    if (!accessToken) {
      return res.status(401).json({ 
        message: 'No access token provided' 
      });
    }

    try {
      const decoded = TokenUtils.verifyAccessToken(accessToken) as {userId: string}
      
      const user = await User.findById(decoded.userId).select('-password -refreshToken');
      
      if (!user) {
        return res.status(401).json({ 
          message: 'User not found' 
        });
      }
      
      req.user = user;
      next();

    } catch (accessError) {
      if (accessError instanceof jwt.TokenExpiredError) {
        return res.status(401).json({ 
          message: 'Access token expired' 
        });
      }
      return res.status(401).json({ 
        message: 'Invalid access token' 
      });
    }

  } catch (error) {
    res.status(500).json({ 
      message: 'Authentication failed' 
    });
  }
};