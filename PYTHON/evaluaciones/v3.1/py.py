import React, { useState, useEffect } from 'react';
import { Upload, Play, ArrowRight, CheckCircle, XCircle, FileText, Award, Clock, Target } from 'lucide-react';

const ModernTriviaGame = () => {
  const [currentScreen, setCurrentScreen] = useState('upload');
  const [file, setFile] = useState(null);
  const [coverImage, setCoverImage] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [studentName, setStudentName] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [responses, setResponses] = useState([]);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [shuffledOptions, setShuffledOptions] = useState([]);
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      parseExcelFile(uploadedFile);
    }
  };

  const handleCoverImageUpload = (e) => {
    const imageFile = e.target.files[0];
    if (imageFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setCoverImage(event.target.result);
      };
      reader.readAsDataURL(imageFile);
    }
  };

  const parseExcelFile = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet);
        
        const formattedQuestions = jsonData.map(row => ({
          pregunta: row.Pregunta || row.pregunta,
          correcta: row['Respuesta Correcta'] || row.correcta,
          incorrectas: [row.R1 || row.r1, row.R2 || row.r2, row.R3 || row.r3]
        }));
        
        setQuestions(formattedQuestions);
      } catch (error) {
        alert('Error al leer el archivo. Verifica que tenga el formato correcto.');
      }
    };
    reader.readAsArrayBuffer(file);
  };

  const startGame = () => {
    if (!studentName.trim()) {
      alert('Por favor ingresa tu nombre');
      return;
    }
    setCurrentScreen('game');
    setStartTime(new Date());
    shuffleCurrentQuestion();
  };

  const shuffleCurrentQuestion = () => {
    if (questions[currentQuestion]) {
      const options = [
        questions[currentQuestion].correcta,
        ...questions[currentQuestion].incorrectas
      ];
      const shuffled = options.sort(() => Math.random() - 0.5);
      setShuffledOptions(shuffled);
    }
  };

  useEffect(() => {
    if (currentScreen === 'game' && questions.length > 0) {
      shuffleCurrentQuestion();
    }
  }, [currentQuestion, currentScreen]);

  const handleAnswer = () => {
    if (!selectedAnswer) {
      alert('Por favor selecciona una respuesta');
      return;
    }

    const isCorrect = selectedAnswer === questions[currentQuestion].correcta;
    
    setResponses([...responses, {
      pregunta: questions[currentQuestion].pregunta,
      respuestaEstudiante: selectedAnswer,
      respuestaCorrecta: questions[currentQuestion].correcta,
      correcta: isCorrect
    }]);

    if (isCorrect) {
      setCorrectAnswers(correctAnswers + 1);
    }

    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer('');
    } else {
      setEndTime(new Date());
      setCurrentScreen('results');
    }
  };

  const skipQuestion = () => {
    setResponses([...responses, {
      pregunta: questions[currentQuestion].pregunta,
      respuestaEstudiante: 'Sin respuesta',
      respuestaCorrecta: questions[currentQuestion].correcta,
      correcta: false
    }]);

    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer('');
    } else {
      setEndTime(new Date());
      setCurrentScreen('results');
    }
  };

  const generateReport = () => {
    const percentage = ((correctAnswers / questions.length) * 100).toFixed(2);
    const duration = endTime && startTime ? Math.round((endTime - startTime) / 1000 / 60) : 0;
    
    let reportHTML = `
      <!DOCTYPE html>
      <html lang="es">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados - ${studentName}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }
          .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
          .cover { position: relative; height: 400px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; flex-direction: column; color: white; text-align: center; padding: 40px; }
          .cover-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.3; }
          .cover-content { position: relative; z-index: 1; }
          .cover h1 { font-size: 48px; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
          .cover .student-name { font-size: 32px; margin-top: 20px; font-weight: 300; }
          .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 40px; background: #f8f9fa; }
          .stat-card { background: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
          .stat-card .icon { font-size: 40px; margin-bottom: 10px; }
          .stat-card .value { font-size: 36px; font-weight: bold; margin: 10px 0; }
          .stat-card .label { color: #666; font-size: 14px; text-transform: uppercase; }
          .correct { color: #10b981; }
          .incorrect { color: #ef4444; }
          .content { padding: 40px; }
          .section-title { font-size: 28px; color: #333; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 3px solid #667eea; }
          .question-block { background: #f8f9fa; padding: 25px; border-radius: 15px; margin-bottom: 25px; border-left: 5px solid #667eea; }
          .question-number { color: #667eea; font-weight: bold; font-size: 18px; margin-bottom: 10px; }
          .question-text { font-size: 18px; color: #333; margin-bottom: 20px; line-height: 1.6; }
          .answer-row { margin: 10px 0; padding: 15px; background: white; border-radius: 10px; display: flex; align-items: center; gap: 10px; }
          .answer-label { font-weight: bold; min-width: 150px; color: #666; }
          .answer-value { flex: 1; }
          .badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }
          .badge.correct { background: #d1fae5; color: #065f46; }
          .badge.incorrect { background: #fee2e2; color: #991b1b; }
          .footer { background: #333; color: white; padding: 30px; text-align: center; }
          .performance { font-size: 24px; margin-top: 20px; padding: 20px; background: white; border-radius: 10px; text-align: center; }
          @media print { body { background: white; padding: 0; } .container { box-shadow: none; } }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="cover">
            ${coverImage ? `<img src="${coverImage}" class="cover-image" alt="Portada">` : ''}
            <div class="cover-content">
              <h1>📚 Resultados del Examen</h1>
              <div class="student-name">${studentName}</div>
              <p style="margin-top: 20px; font-size: 18px;">${new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>
          </div>
          
          <div class="stats">
            <div class="stat-card">
              <div class="icon">🎯</div>
              <div class="value">${questions.length}</div>
              <div class="label">Total Preguntas</div>
            </div>
            <div class="stat-card">
              <div class="icon">✅</div>
              <div class="value correct">${correctAnswers}</div>
              <div class="label">Correctas</div>
            </div>
            <div class="stat-card">
              <div class="icon">❌</div>
              <div class="value incorrect">${questions.length - correctAnswers}</div>
              <div class="label">Incorrectas</div>
            </div>
            <div class="stat-card">
              <div class="icon">📊</div>
              <div class="value" style="color: ${percentage >= 70 ? '#10b981' : '#ef4444'}">${percentage}%</div>
              <div class="label">Porcentaje</div>
            </div>
            <div class="stat-card">
              <div class="icon">⏱️</div>
              <div class="value">${duration}</div>
              <div class="label">Minutos</div>
            </div>
          </div>

          <div class="content">
            <div class="performance">
              ${percentage >= 90 ? '🌟 ¡Excelente trabajo! Dominaste el tema.' : 
                percentage >= 70 ? '👍 ¡Buen trabajo! Vas por buen camino.' : 
                percentage >= 50 ? '📚 Puedes mejorar. Sigue estudiando.' : 
                '💪 Sigue practicando. ¡No te rindas!'}
            </div>

            <h2 class="section-title">📝 Detalle de Respuestas</h2>
            ${responses.map((resp, idx) => `
              <div class="question-block">
                <div class="question-number">Pregunta ${idx + 1}</div>
                <div class="question-text">${resp.pregunta}</div>
                <div class="answer-row">
                  <span class="answer-label">Tu respuesta:</span>
                  <span class="answer-value" style="color: ${resp.correcta ? '#10b981' : '#ef4444'}; font-weight: bold;">
                    ${resp.respuestaEstudiante}
                  </span>
                  <span class="badge ${resp.correcta ? 'correct' : 'incorrect'}">
                    ${resp.correcta ? '✓ Correcto' : '✗ Incorrecto'}
                  </span>
                </div>
                ${!resp.correcta ? `
                  <div class="answer-row">
                    <span class="answer-label">Respuesta correcta:</span>
                    <span class="answer-value" style="color: #10b981; font-weight: bold;">
                      ${resp.respuestaCorrecta}
                    </span>
                  </div>
                ` : ''}
              </div>
            `).join('')}
          </div>

          <div class="footer">
            <p style="font-size: 18px; margin-bottom: 10px;">Generado automáticamente por Sistema de Evaluación</p>
            <p style="color: #aaa;">© ${new Date().getFullYear()} - Todos los derechos reservados</p>
          </div>
        </div>
      </body>
      </html>
    `;

    const blob = new Blob([reportHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Resultados_${studentName}_${new Date().getTime()}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Upload Screen
  if (currentScreen === 'upload') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12 animate-fade-in">
            <div className="text-6xl mb-4">🎓</div>
            <h1 className="text-5xl font-bold text-white mb-4">Sistema de Evaluación Moderno</h1>
            <p className="text-xl text-white/90">Carga tus preguntas y comienza tu examen</p>
          </div>

          <div className="bg-white rounded-3xl shadow-2xl p-8 mb-6">
            <div className="mb-8">
              <label className="block text-lg font-semibold text-gray-700 mb-4">
                📄 Archivo de Preguntas (Excel)
              </label>
              <div className="border-3 border-dashed border-indigo-300 rounded-2xl p-8 text-center hover:border-indigo-500 transition-all bg-indigo-50">
                <Upload className="w-16 h-16 mx-auto mb-4 text-indigo-500" />
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="excel-upload"
                />
                <label htmlFor="excel-upload" className="cursor-pointer">
                  <span className="text-lg text-gray-700">
                    {file ? `✓ ${file.name}` : 'Click para seleccionar archivo Excel'}
                  </span>
                </label>
              </div>
            </div>

            <div className="mb-8">
              <label className="block text-lg font-semibold text-gray-700 mb-4">
                🖼️ Imagen de Portada (Opcional)
              </label>
              <div className="border-3 border-dashed border-purple-300 rounded-2xl p-8 text-center hover:border-purple-500 transition-all bg-purple-50">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleCoverImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="cursor-pointer">
                  {coverImage ? (
                    <img src={coverImage} alt="Portada" className="max-h-40 mx-auto rounded-lg mb-2" />
                  ) : (
                    <FileText className="w-16 h-16 mx-auto mb-4 text-purple-500" />
                  )}
                  <span className="text-lg text-gray-700">
                    {coverImage ? '✓ Imagen cargada' : 'Click para seleccionar imagen'}
                  </span>
                </label>
              </div>
            </div>

            {questions.length > 0 && (
              <div className="bg-green-50 border-2 border-green-500 rounded-2xl p-6 mb-6">
                <p className="text-center text-green-800 text-lg font-semibold">
                  ✓ {questions.length} preguntas cargadas correctamente
                </p>
              </div>
            )}

            <button
              onClick={() => setCurrentScreen('name')}
              disabled={questions.length === 0}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-2xl font-bold text-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg flex items-center justify-center gap-3"
            >
              Continuar <ArrowRight />
            </button>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-white">
            <p className="text-sm mb-2"><strong>Formato del Excel:</strong></p>
            <p className="text-sm">Columnas: Pregunta, Respuesta Correcta, R1, R2, R3</p>
          </div>
        </div>
      </div>
    );
  }

  // Name Screen
  if (currentScreen === 'name') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-8">
        <div className="bg-white rounded-3xl shadow-2xl p-12 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">👤</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">¡Bienvenido!</h2>
            <p className="text-gray-600">Prepárate para {questions.length} preguntas</p>
          </div>

          <input
            type="text"
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            placeholder="Ingresa tu nombre completo"
            className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-2xl mb-6 focus:outline-none focus:border-indigo-500 transition-all"
            onKeyPress={(e) => e.key === 'Enter' && startGame()}
          />

          <button
            onClick={startGame}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-2xl font-bold text-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg flex items-center justify-center gap-3"
          >
            <Play className="w-6 h-6" />
            Comenzar Examen
          </button>
        </div>
      </div>
    );
  }

  // Game Screen
  if (currentScreen === 'game') {
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-t-3xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-semibold text-gray-700">
                Pregunta {currentQuestion + 1} de {questions.length}
              </span>
              <span className="text-lg font-semibold text-indigo-600">
                ✓ {correctAnswers} correctas
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-b-3xl shadow-2xl p-8 mb-6">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 leading-relaxed">
                {questions[currentQuestion]?.pregunta}
              </h3>

              <div className="space-y-4">
                {shuffledOptions.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedAnswer(option)}
                    className={`w-full p-5 text-left rounded-2xl border-2 transition-all text-lg ${
                      selectedAnswer === option
                        ? 'border-indigo-500 bg-indigo-50 shadow-lg scale-105'
                        : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                    }`}
                  >
                    <span className="font-semibold text-indigo-600 mr-3">
                      {String.fromCharCode(65 + idx)}.
                    </span>
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleAnswer}
                className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-2xl font-bold text-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" />
                Responder
              </button>
              <button
                onClick={skipQuestion}
                className="flex-1 bg-gradient-to-r from-orange-400 to-orange-500 text-white py-4 rounded-2xl font-bold text-lg hover:from-orange-500 hover:to-orange-600 transition-all shadow-lg flex items-center justify-center gap-2"
              >
                <ArrowRight className="w-5 h-5" />
                Saltar
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Results Screen
  if (currentScreen === 'results') {
    const percentage = ((correctAnswers / questions.length) * 100).toFixed(2);

    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-3xl shadow-2xl p-12 text-center">
            <div className="text-7xl mb-6">
              {percentage >= 90 ? '🌟' : percentage >= 70 ? '👍' : percentage >= 50 ? '📚' : '💪'}
            </div>
            <h2 className="text-4xl font-bold text-gray-800 mb-4">¡Examen Completado!</h2>
            <p className="text-2xl text-gray-600 mb-8">{studentName}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-indigo-50 p-6 rounded-2xl">
                <Target className="w-10 h-10 mx-auto mb-2 text-indigo-600" />
                <div className="text-3xl font-bold text-indigo-600">{questions.length}</div>
                <div className="text-sm text-gray-600">Preguntas</div>
              </div>
              <div className="bg-green-50 p-6 rounded-2xl">
                <CheckCircle className="w-10 h-10 mx-auto mb-2 text-green-600" />
                <div className="text-3xl font-bold text-green-600">{correctAnswers}</div>
                <div className="text-sm text-gray-600">Correctas</div>
              </div>
              <div className="bg-red-50 p-6 rounded-2xl">
                <XCircle className="w-10 h-10 mx-auto mb-2 text-red-600" />
                <div className="text-3xl font-bold text-red-600">{questions.length - correctAnswers}</div>
                <div className="text-sm text-gray-600">Incorrectas</div>
              </div>
              <div className={`${percentage >= 70 ? 'bg-green-50' : 'bg-red-50'} p-6 rounded-2xl`}>
                <Award className={`w-10 h-10 mx-auto mb-2 ${percentage >= 70 ? 'text-green-600' : 'text-red-600'}`} />
                <div className={`text-3xl font-bold ${percentage >= 70 ? 'text-green-600' : 'text-red-600'}`}>
                  {percentage}%
                </div>
                <div className="text-sm text-gray-600">Porcentaje</div>
              </div>
            </div>

            <div className={`p-6 rounded-2xl mb-8 ${percentage >= 70 ? 'bg-green-50' : 'bg-orange-50'}`}>
              <p className="text-xl font-semibold text-gray-800">
                {percentage >= 90 ? '¡Excelente trabajo! Dominaste el tema.' : 
                 percentage >= 70 ? '¡Buen trabajo! Vas por buen camino.' : 
                 percentage >= 50 ? 'Puedes mejorar. Sigue estudiando.' : 
                 '¡Sigue practicando! No te rindas.'}
              </p>
            </div>

            <button
              onClick={generateReport}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-2xl font-bold text-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg flex items-center justify-center gap-3"
            >
              <FileText className="w-6 h-6" />
              Descargar Reporte Completo
            </button>
          </div>
        </div>
      </div>
    );
  }
};

export default ModernTriviaGame;