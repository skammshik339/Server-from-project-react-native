export interface TransposeResponse {
  message: string;
  file: {
    originalName: string;
    savedAs: string;
    path: string;
    size: number;
  };
  result?: {
    url: string;
    path: string;
    name: string;
    size?: number;
  };
  nextStep: string;
}

export interface ErrorResponse {
  error: string;
  details?: string;
}