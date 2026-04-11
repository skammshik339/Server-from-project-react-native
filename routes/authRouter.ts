import express from 'express';
import { register, login, logout, getMe, refreshToken, verifyEmail, checkVerificationStatus } from '../controllers/authController';
import { authMiddleware } from '../middleware/auth';

const router = express.Router();

router.post('/register', register);
router.post('/login', login);
router.post('/logout', authMiddleware, logout);
router.get('/me', authMiddleware, getMe);
router.post('/refresh', refreshToken);
router.get('/verify-email', verifyEmail);
router.get('/verification-status/:userId', checkVerificationStatus);

export default router; 