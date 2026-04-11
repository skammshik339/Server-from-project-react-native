import express from 'express';
import { upload } from '../config/multer';
import { exec } from 'child_process';
import path from 'path';
import Transposition from '../models/transpositionModel';
import { authMiddleware } from '../middleware/auth';
import User from '../models/User'

const router = express.Router();

router.post('/', authMiddleware, upload.single('file'), async (req: any, res: any) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Файл не загружен' });
    }

    const userId = req.user?._id;
    if (!userId) {
      return res.status(401).json({ error: 'Пользователь не авторизован' });
    }  

    const semitones = req.query.semitones ? parseInt(req.query.semitones) : -2;

    const filePath = req.file.path;
   const pythonScript = path.join(process.cwd(), 'dist', 'python', 'processor.py');


    const pythonPath = 'python3';


    exec(`"${pythonPath}" "${pythonScript}" "${filePath}" ${semitones}`, async (error, stdout, stderr) => {
      if (error) {
        console.error('python error:', error);
        return res.status(500).json({ error: 'Ошибка обработки' });
      }

      try {
        const cleanStdout = stdout.trim();
        const result = JSON.parse(cleanStdout);

        if (!result.success) {
          return res.status(500).json({ error: result.error });
        }

        const transposition = new Transposition({
          userId,
          name: req.file!.originalname,
          images: result.output_files.map((file: any, index: number) => ({
            url: file.url,
            page: index + 1
          }))
        });

        await transposition.save();

        res.json({
          message: 'Готово',
          transposition: {
            id: transposition._id,
            name: transposition.name,
            images: transposition.images,
            createdAt: transposition.createdAt
          }
        });

      } catch (e) {
        console.error('Ошибка:', e);
        res.status(500).json({ error: 'Ошибка ответа от Python' });
      }
    });

  } catch (err) {
    console.error('server error:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/history', authMiddleware, async (req: any, res: any) => {
  try {
    const userId = req.user?._id;
    const history = await Transposition.find({ userId })
      .sort({ createdAt: -1 })
      .limit(50)
     .select('_id name images createdAt');


    res.json({ history });
  } catch (error) {
    res.status(500).json({ error: 'Ошибка загрузки истории' });
  }
});

router.get('/all', authMiddleware, async (req: any, res: any) => {
  try {
    const transpositions = await Transposition.find()
      .sort({ createdAt: -1 })
      .select('_id name images createdAt');

    res.json({ transpositions });
  } catch (error) {
    res.status(500).json({ error: 'Ошибка загрузки транспозиций' });
  }
});

router.get('/user/:userId', authMiddleware, async (req: any, res: any) => {
  try {
    const userId = req.params.userId;

    const targetUser = await User.findById(userId);
    if (!targetUser) {
      return res.status(404).json({ error: 'Пользователь не найден' });
    }

    const transpositions = await Transposition.find({ userId })
      .sort({ createdAt: -1 })
      .select('_id name images createdAt');

    res.json({ transpositions });
  } catch (error) {
    res.status(500).json({ error: 'Ошибка загрузки транспозиций' });
  }
});

export default router;