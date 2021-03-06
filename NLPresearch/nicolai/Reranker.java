import java.io.*;
import java.util.*;
import java.nio.charset.Charset;

class Reranker {
//jar cmf Reranker.mf Reranker.jar Reranker.class
	public static void main(String[] args) {
		String predictionFile;		// *.phraseOut
		String paradigmFile; 		// output
		String tagFile; 			
		boolean iterative = false; 	 //deprecated
		boolean pipes = true; 		//default
		boolean modify = false;		//deprecated
		String modFile = ""; 		//deprecated

		String goldFile; 			//answer file
		String countFile = ""; 		//corpus counts, unused
		String LMFile = ""; 		//unused
		String rerankerScoreFile = ""; //deprecated
		String word2vecFile = "";	//deprecated
		int vectorSize = 0; 		//deprecated
		int nBest; 
		boolean test; 		//false for training, true for testing
		boolean useAlignmentScore = true; //default
		boolean useCorpus = false;   //unused
		boolean useLM = false;	     //unused
		boolean intersection = true; //default
		boolean useWord2Vec = false; //deprecated
		String outFile; 			 // output
		
		String mode = "";
		try {
			mode = args[0];
		} catch (Exception e) {
			System.err.println("Reranker usage: {'extract'|'construct'} [params]");
			System.exit(1);
		}
		if (mode.equals("extract")) {
			try {
				predictionFile = args[1];
				paradigmFile = args[2];
				tagFile = args[3];
				extractParadigms(predictionFile, paradigmFile, tagFile, iterative,
						pipes, modify, modFile);
			} catch (Exception e) {
				System.err.println("extractParadigms usage: 'extract' predictionFile paradigmFile tagFile");
			}
		}
		else if (mode.equals("construct")) {
			try {
				predictionFile = args[1];
				paradigmFile = args[2];
				tagFile = args[3];
				goldFile = args[4];
				nBest = Integer.parseInt(args[5]);
				test =  Boolean.parseBoolean(args[6]);
				outFile = args[7];
				/* Other flags
				useAlignmentScore = t
				useCorpus = f/t
				useLM = f/t
				intersection = 	t
				iterative = f
				useWord2Vec = f
				*/
				constructSVMFileShortTwoModels(predictionFile, predictionFile,
						paradigmFile, paradigmFile, goldFile, tagFile, countFile, 
						LMFile, LMFile, rerankerScoreFile, word2vecFile, vectorSize,
						nBest, test, useAlignmentScore, useCorpus, useLM, intersection,
						iterative, useWord2Vec, outFile);		
			} catch (Exception e) {
				System.err.println("constructModels usage: 'construct' predictionFile paradigmFile tagFile goldFile nBest test outFile");
			}
		}
		else {
			System.err.println("Reranker usage: {'extract'|'construct'} [params]");
		}
	}

	private static void extractParadigms(String predictionFile,
			String paradigmFile, String tagFile, boolean iterative,
			boolean pipes, boolean modify, String modifiedFile) {
		try {
			
			//get lang_pos combo and put it in UTF-8 for printing
			String[] noExtRA = predictionFile.split("\\.");
			String noExt = noExtRA[0];
			String[] fname = noExt.split("/");
			String language = fname[fname.length - 1];
			byte[] utf8Bytes = language.getBytes(Charset.forName("UTF-8"));
		    language = new String(utf8Bytes, Charset.forName("UTF-8"));
		    language = language.replaceAll("_", " ");

		    System.out.println("Extracting paradigms for: " + language);

			BufferedReader input = new BufferedReader(new InputStreamReader(
					new FileInputStream(predictionFile), "UTF-8"));
			BufferedWriter output = new BufferedWriter(new OutputStreamWriter(
					new FileOutputStream(paradigmFile), "UTF-8"));
			BufferedWriter output2 = null;

			BufferedReader tagInput = new BufferedReader(new InputStreamReader(
					new FileInputStream(tagFile), "UTF-8"));
			if (modify) {
				output2 = new BufferedWriter(new OutputStreamWriter(
						new FileOutputStream(modifiedFile), "UTF-8"));

			}
			String currentLine;

			Hashtable<String, TreeMap<String, String>> lemmas = new Hashtable<String, TreeMap<String, String>>();
			HashSet<String> tagSet = new HashSet<String>();
			Double maxScore = 0.0;
			while ((currentLine = tagInput.readLine()) != null) {
				tagSet.add(currentLine);
			}
			tagInput.close();
			//Random generator = new Random();
			while ((currentLine = input.readLine()) != null) {
				String[] words = currentLine.split("\\t");
				String[] parts = words[0].split("\\+");
				if (iterative) {
					parts = words[1].split("\\+");
				}
				String lemma = "";
				if (parts.length == 3) {
					lemma = parts[1].trim();
				}

				//most common form
				else if (parts.length == 2) {
					lemma = parts[0].trim().replaceAll("\\|", "");
				}

				if (lemma.startsWith("|")) {
					lemma = lemma.substring(1).replaceAll("\\|", "");
				}
				TreeMap<String, String> forms = new TreeMap<String, String>();
				// new lemma
				if (lemmas.get(lemma) == null) {
					if (currentLine.equals("")) {
						continue;
					}
					if (words.length > 2) {
						//if forms pair is not best, do nothing
						if (!words[2].equals("1")) {
							continue;
						}
					}
					if (!iterative) {
						forms.put(words[0], words[1]);
					} else {
						forms.put(words[1], words[2]);
						maxScore = Double.parseDouble(words[0]);
					}
				} else {
					forms = lemmas.get(lemma);
					// new form for old lemma
					if (!iterative && forms.get(words[0]) == null) {
						if (words.length <= 2
								|| words[2].equals("1")) {
							String tag = parts[parts.length - 1].replaceAll("\\|", "");
							// if valid tag, add form pair to forms
							if (tagSet.contains(tag)) {
								forms.put(words[0], words[1]);
							}
							else {
								System.out.println("Tag not in " + language + " paradigm: " + tag);
							}
						}
					}
					else if (iterative) {
						if (forms.get(words[1]) == null
								|| Double.parseDouble(words[0]) > maxScore) {
							maxScore = Double.parseDouble(words[0]);
							forms.put(words[1], words[2]);
						}
					}
				}
				lemmas.put(lemma, forms);	
			}
			input.close();

			for (String current : lemmas.keySet()) {
				output.write("Lemma:\t"
						+ current.replaceAll("\\|", "").replaceAll("_", "")
						+ "\n");
				TreeMap<String, String> sortedMap = lemmas.get(current);
				//TagComparator bvc = new TagComparator(forms, tagSet);
				//TreeMap<String, String> sortedMap = new TreeMap<String, String>(bvc);
				//sortedMap.putAll(forms);

				for (String currentForm : sortedMap.keySet()) {
					if (pipes) {
						output.write("\t" + currentForm/*
														 * .replaceAll("\\|",
														 * "").replaceAll("_",
														 * "")
														 */+ "\t"
								+ sortedMap.get(currentForm)/*
														 * .replaceAll("\\|",
														 * "").replaceAll("_",
														 * "")
														 */+ "\n");
					} else {
						output.write("\t"
								+ currentForm.replaceAll("\\|", " ")
										.replaceAll("_", "")
								+ "\t"
								+ sortedMap.get(currentForm).replaceAll("\\|", " ")
										.replaceAll("_", "") + "\n");
					}
					if (sortedMap.size() == tagSet.size() && output2 != null) {
						output2.write(currentForm.replaceAll("\\|", " ")
								.replaceAll("_", "")
								+ "\t"
								+ sortedMap.get(currentForm).replaceAll("\\|", " ")
										.replaceAll("_", "") + "\n");
					}
				}
			}
			output.close();
			if (output2 != null) {
				output2.close();
			}
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}

	private static void constructSVMFileShortTwoModels(String predictionFile,
			String secondPredictionFile, String paradigmFile,
			String secondParadigmFile, String goldFile, String tagFile,
			String countFile, String LMFile, String secondLMFile,
			String rerankerScoreFile, String word2vecFile, int vectorSize,
			int nBest, boolean test, boolean useAlignmentScore,
			boolean useCorpus, boolean useLM, boolean intersection,
			boolean iterative, boolean useWord2Vec, String outFile) {
		// We only consider 3 features for each n*n comparison: is the ending
		// (suffix) the same?
		// Is the stem (not affix) the same, and is the whole word the same?

		// Now, we also use two models, so we have double the features:
		// They are the same, but separate for each model.
		// There is a lot of repetitious code in this function; basically,
		// whatever we do for the first model, we do for the second

		try {
			int corpusIndex = 0;
			int alignmentIndex = 0;
			int alignmentIndex2 = 0;
			int LMIndex = 0;
			int rrIndex = 0;
			int w2vOffset = 0;

			//String maxScore = "";
			Integer maxIndex = 0;
			Integer features = 0;

			//get lang_pos combo and put it in UTF-8 for printing
			String[] noExtRA = predictionFile.split("\\.");
			String noExt = noExtRA[0];
			String[] fname = noExt.split("/");
			String language = fname[fname.length - 1];
			byte[] utf8Bytes = language.getBytes(Charset.forName("UTF-8"));
		    language = new String(utf8Bytes, Charset.forName("UTF-8"));
		    language = language.replaceAll("_", " ");

		    if (test) {    	
		    	System.out.println("Constructing models for: " + language);
		    }

			BufferedReader predictionInput = new BufferedReader(
					new InputStreamReader(new FileInputStream(predictionFile),
							"UTF-8"));

			BufferedReader secondPredictionInput = new BufferedReader(
					new InputStreamReader(new FileInputStream(
							secondPredictionFile), "UTF-8"));

			BufferedReader RRScoreInput = null;

			if (iterative) {
				RRScoreInput = new BufferedReader(new InputStreamReader(
						new FileInputStream(rerankerScoreFile), "UTF-8"));
			}

			BufferedReader paradigmInput = new BufferedReader(
					new InputStreamReader(new FileInputStream(paradigmFile),
							"UTF-8"));

			//BufferedReader secondParadigmInput = new BufferedReader(
			//		new InputStreamReader(new FileInputStream(
			//				secondParadigmFile), "UTF-8"));

			BufferedReader goldInput = new BufferedReader(
					new InputStreamReader(new FileInputStream(goldFile), "UTF-8"));

			BufferedReader countInput = null;
			if (useCorpus) {
				countInput = new BufferedReader(new InputStreamReader(
						new FileInputStream(countFile), "UTF-8"));
			}

			BufferedReader LMInput = null;
			BufferedReader secondLMInput = null;
			if (useLM) {
				LMInput = new BufferedReader(new InputStreamReader(
						new FileInputStream(LMFile), "UTF-8"));
	
				secondLMInput = new BufferedReader(new InputStreamReader(
						new FileInputStream(secondLMFile), "UTF-8"));
			}
			
			BufferedReader tagInput = new BufferedReader(new InputStreamReader(
					new FileInputStream(tagFile), "UTF-8"));

			BufferedWriter output = new BufferedWriter(new OutputStreamWriter(
					new FileOutputStream(outFile), "UTF-8"));

			int offset = 0;
			int qid = 0;

			Random generator = new Random();
			Hashtable<String, ArrayList<String>> paradigms = new Hashtable<String, ArrayList<String>>();
			//Hashtable<String, ArrayList<String>> secondParadigms = new Hashtable<String, ArrayList<String>>();
			Hashtable<String, Integer> tagsInParadigm = new Hashtable<String, Integer>();

			Hashtable<String, Integer> counts = new Hashtable<String, Integer>();
			Hashtable<String, Double> LM = new Hashtable<String, Double>();
			Hashtable<String, Double> secondLM = new Hashtable<String, Double>();
			Hashtable<String, Double> rrScores = new Hashtable<String, Double>();
			Hashtable<String, Hashtable<String, String>> secondPredictions = new Hashtable<String, Hashtable<String, String>>();

			Hashtable<String, String> w2vScores = new Hashtable<String, String>();

			String currentLine;
			String currentInflection = "";
			//String currentScore = "";

			while ((currentLine = tagInput.readLine()) != null) {
				tagsInParadigm.put(currentLine, tagsInParadigm.size());
			}
			tagInput.close();

			if (iterative) {
				while ((currentLine = RRScoreInput.readLine()) != null) {
					String[] words = currentLine.split("\\t");
					Double score = Double.parseDouble(words[0]);
					rrScores.put(
							words[1].replaceAll("\\||_", "")
									+ words[2].replaceAll("\\||_", ""), score);
				}
			}

			BufferedReader w2vInput = null;
			String oovVector = "";

			if (useWord2Vec) {
				w2vInput = new BufferedReader(new InputStreamReader(
						new FileInputStream(word2vecFile), "UTF-8"));
				oovVector = "$OOV$";
				double L2Norm = 0.0;
				for (int i = 0; i < vectorSize; i++) {
					Double value = generator.nextGaussian();
					L2Norm += Math.pow(value, 2);
					oovVector += " " + Double.toString(value);
				}
				L2Norm = Math.sqrt(L2Norm);
				String[] vectorParts = oovVector.split(" ");
				oovVector = "$OOV$";
				for (int i = 1; i < vectorParts.length; i++) {
					Double value = Double.parseDouble(vectorParts[i]) / L2Norm;
					oovVector += " " + Double.toString(value);
				}

				while ((currentLine = w2vInput.readLine()) != null) {
					String[] words = currentLine.split(" ");
					//double L2norm = 0.0;

					/*
					 * for(int i = 1; i < words.length; i++) { L2norm +=
					 * Math.pow(Double.parseDouble(words[i]), 2); }
					 */

					// L2norm = Math.sqrt(L2norm);
					// String outString = words[0];
					/*
					 * for(int i = 1; i < words.length; i++) { double value =
					 * Double.parseDouble(words[i]) / L2norm; outString += " " +
					 * Double.toString(value); }
					 */
					w2vScores.put(words[0], currentLine);

				}
			}

			while ((currentLine = secondPredictionInput.readLine()) != null) {
				if (currentLine.equals("")) {
					continue;
				}

				// String currentStem = secondStemInput.readLine();
				String[] words = currentLine.split("\\t");
				// String [] stemWords = currentStem.split("\\t");
				String input = words[0].replaceAll("\\||_", "");
				String prediction = words[1].replaceAll("\\||_", "");
				Hashtable<String, String> currentPredictions;
				if (!secondPredictions.containsKey(input)) {
					currentPredictions = new Hashtable<String, String>();
				} else {
					currentPredictions = secondPredictions.get(input);
				}
				
				if (!currentPredictions.containsKey(prediction)) {
					currentPredictions.put(prediction, currentLine + "\t");// +
																			// stemWords[1]);
				}

				secondPredictions.put(input, currentPredictions);

			}
			secondPredictionInput.close();
			if (useCorpus) {
				while ((currentLine = countInput.readLine()) != null) {
					String[] words = currentLine.toLowerCase().split("\\t");
					counts.put(words[0], Integer.parseInt(words[1]));
				}
				countInput.close();
			}

			if (useLM) {
				while ((currentLine = LMInput.readLine()) != null) {
					String[] words = currentLine.split("\\t");
					LM.put(words[0], Double.parseDouble(words[1]));
				}
				LMInput.close();

				while ((currentLine = secondLMInput.readLine()) != null) {
					String[] words = currentLine.split("\\t");
					secondLM.put(words[0], Double.parseDouble(words[1]));
				}
				secondLMInput.close();
			}

			while ((currentLine = paradigmInput.readLine()) != null) {
				if (!currentLine.startsWith("\t")) {
					//int z = tagsInParadigm.size();

					if (!currentInflection.equals("")) {
						ArrayList<String> currentTable = paradigms
								.get(currentInflection);

						while ((currentTable.size() < tagsInParadigm.size())) {
							currentTable.add("" + "\t" + "");
						}
						paradigms.put(currentInflection, currentTable);
					}
					String[] words = currentLine.split("\\t");
					currentInflection = words[1];
					ArrayList<String> currentTable = new ArrayList<String>();
					paradigms.put(currentInflection, currentTable);
				}

				else {
					//if (currentInflection.equals("atmen")) {
					//	int l = 0;
					//}
					String[] words = currentLine.split("\\t");
					//if (words[1].contains("LV")) {
					//	int l = 0;
					//}
					ArrayList<String> currentTable = paradigms
							.get(currentInflection);
					String[] parts = words[1].split("\\+");
					String tag = parts[parts.length - 1].replaceAll("\\|", "");
					if(tagsInParadigm.get(tag) == null)
					{
						System.out.println("Tag not in " + language + " paradigm: " + tag);
					}
					else {
						while (tagsInParadigm.get(tag) > currentTable.size()) {
							currentTable.add("" + "\t" + "");
						}
					}
					currentTable.add(words[1] + "\t"
							+ words[2].replaceAll(" ", ""));
					paradigms.put(currentInflection, currentTable);

				}
			}

			if (!currentInflection.equals("")) {
				ArrayList<String> currentTable = paradigms
						.get(currentInflection);

				while ((currentTable.size() < tagsInParadigm.size())) {
					currentTable.add("" + "\t" + "");
				}
				paradigms.put(currentInflection, currentTable);
			}
			paradigmInput.close();
			/*
			 * while((currentLine = secondParadigmInput.readLine()) != null) {
			 * if(!currentLine.startsWith("\t")) { String [] words=
			 * currentLine.split("\\t"); currentInflection = words[1];
			 * ArrayList<String> currentTable = new ArrayList<String>();
			 * secondParadigms.put(currentInflection, currentTable); } else {
			 * if(currentInflection.equals("akkreditieren")) { int l = 0; }
			 * String [] words = currentLine.split("\\t");
			 * if(words[1].contains("LV")) { int l = 0; } ArrayList<String>
			 * currentTable = secondParadigms.get(currentInflection);
			 * currentTable.add(words[1] + "\t" + words[2].replaceAll(" ", ""));
			 * secondParadigms.put(currentInflection, currentTable);
			 * 
			 * } } secondParadigmInput.close();
			 */

			Hashtable<String, String> goldForm = new Hashtable<String, String>();

			while ((currentLine = goldInput.readLine()) != null) {
				String[] words = currentLine.replaceAll("\\|", "").split("\\t");
				//String[] parts = words[0].split("\\+");
				try {	
					if (goldForm.get(words[0]) == null) {
						//if (words[0].contains("tuschieren")) {	
						//}
						goldForm.put(words[0], words[1].replaceAll(" ", ""));
					}
				} catch (IndexOutOfBoundsException e) {
    				System.out.println("Couldn't find answer in GoldFile for " + language + " input: " + words[0]);
    			}
			}

			goldInput.close();

			ArrayList<Hashtable<Integer, String>> featureLine = new ArrayList<Hashtable<Integer, String>>();

			while ((currentLine = predictionInput.readLine()) != null) {
				if (currentLine.equals("")) {
					continue;
				}
				ArrayList<String> predictionList = new ArrayList<String>();
				ArrayList<String> predictionSet = new ArrayList<String>();
				ArrayList<Double> predictionScores = new ArrayList<Double>();

				int goldFormIndex = -1; // notFound
				String[] words = currentLine.replaceAll(" ", "").split("\\t");
				// String [] stemWords = currentStem.split("\\t");

				String temp = goldForm.get(words[0].replaceAll("\\|", ""));
				if (temp == null) {
					//int w = 0;
					System.out.println("Couldn't find answer in GoldFile for " + language + " input: " + words[0]);
					continue;
				}
				//if (words.length < 2) {
				//	int w = 0;
				//}
				if (temp.equals(
						words[1].replaceAll("\\||_", ""))) {
					goldFormIndex = 0; //found at initial position
				}

				/*
				 * if(stemWords.length < 2) { System.out.println(currentStem); }
				 */if (secondPredictions.get(words[0]) == null) {
					predictionList.add(words[0] + "\t" + words[1]);// + "\t" +
																	// stemWords[1]);//currentLine.replaceAll(" ",
																	// "").replaceAll("\\|","").replaceAll("_",""));
					predictionSet.add(words[1].replaceAll("\\||_", ""));
					predictionScores.add(Double.parseDouble(words[3]));
				} else if (!intersection
						|| secondPredictions.get(
								words[0].replaceAll("\\||_", "")).get(
								words[1].replaceAll("\\|_", "")) == null) {
					predictionList.add(words[0] + "\t" + words[1]);// + "\t" +
																	// stemWords[1]);//currentLine.replaceAll(" ",
																	// "").replaceAll("\\|","").replaceAll("_",""));
					predictionSet.add(words[1].replaceAll("\\||_", ""));
					predictionScores.add(Double.parseDouble(words[3]));
				}
				//String tempGold = goldForm.get(words[0].replaceAll("\\|", ""));

				qid++;
				String lemma = "";
				for (int i = 1; i < nBest; i++) {

					currentLine = predictionInput.readLine();
					//if (i > 5) {
						// continue;
					//}
					if (currentLine.equals("")) {
						break;
					}
					words = currentLine.replaceAll(" ", "").split("\\t");
					lemma = words[0];
					// stemWords = currentStem.split("\\t");

					//if (goldForm.get(words[0].replaceAll("\\|", "")) == null) {
					//	int w = 0;
					//}
					temp = goldForm.get(words[0].replaceAll("\\|", ""));
					//String temp3 = words[1].replaceAll("\\||_", "");
					if (goldForm.get(words[0].replaceAll("\\|", "")).equals(
							words[1].replaceAll("\\||_", ""))
							&& goldFormIndex < 0) {
						goldFormIndex = i; //match at position i
					}
					/*
					 * if(stemWords.length < 2) {
					 * System.out.println(currentStem); }
					 */
					if (!predictionSet.contains(words[1]
							.replaceAll("\\||_", ""))) {
						if (secondPredictions.get(words[0]) == null) {
							predictionList.add(words[0] + "\t" + words[1]);// +
																			// "\t"
																			// +
																			// stemWords[1]);//currentLine.replaceAll(" ",
																			// "").replaceAll("\\|","").replaceAll("_",""));
							predictionSet.add(words[1].replaceAll("\\||_", ""));
							predictionScores.add(Double.parseDouble(words[3]));
						}

						else if (!intersection
								|| secondPredictions.get(
										words[0].replaceAll("\\||_", "")).get(
										words[1].replaceAll("\\|_", "")) == null) {
							predictionList.add(words[0] + "\t" + words[1]);// +
																			// "\t"
																			// +
																			// stemWords[1]);//currentLine.replaceAll(" ",
																			// "").replaceAll("\\|","").replaceAll("_",""));
							predictionScores.add(Double.parseDouble(words[3]));
							predictionSet.add(words[1].replaceAll("\\||_", ""));
						}
					}

				}

				int firstIndex = predictionList.size();
				Hashtable<String, String> secondPredictionList = secondPredictions
						.get(lemma.replaceAll("\\||_", ""));

				int two = 0;
				if (!intersection) {
					for (String current : secondPredictionList.keySet()) {
						words = secondPredictionList.get(current).split("\\t");
						if (!predictionSet.contains(words[1].replaceAll(
								"\\||_", ""))) {
							predictionList.add(words[0] + "\t" + words[1]);// +
																			// "\t"
																			// +
																			// stemWords[1]);//currentLine.replaceAll(" ",
																			// "").replaceAll("\\|","").replaceAll("_",""));
							predictionSet.add(words[1].replaceAll("\\||_", ""));
						}

						if (goldForm.get(words[0].replaceAll("\\|", ""))
								.equals(words[1].replaceAll("\\||_", ""))
								&& goldFormIndex < 0) {
							goldFormIndex = two + firstIndex;
						}

						two++;

					}
				}

				featureLine = new ArrayList<Hashtable<Integer, String>>();
				if (goldFormIndex < 0 && !test) {
					continue;
					/*
					for (String current : predictionList) {
						words = current.split("\\t");
						String[] parts = words[0].split("\\+");
						maxScore = words[3];
						int size = 0;
						if (parts.length == 3) {
							size = paradigms
									.get(parts[1].substring(1).replaceAll(
											"\\|", "")).size();
						} else if (parts.length == 2) {
							size = paradigms
									.get(parts[0].replaceAll("\\|", "")).size();
						}

					}
					*/
				}
				else {
					for (int c = 0; c < predictionList.size(); c++) {
						//if (c > 5) {
							// continue;
						//}
						//Double AlignmentSum = 0.0;
						String current = predictionList.get(c);
						String[] currentParts = null;
						/* currentParts = current.split("\\t"); */
						String[] currentSplit = current.split("\\t");

						String secondCurrent = "";
						if (secondPredictions.get(currentSplit[0].replaceAll(
								"\\||_", "")) != null) {
							secondCurrent = secondPredictions.get(
									currentSplit[0].replaceAll("\\||_", ""))
									.get(currentSplit[1].replaceAll("\\|", ""));
						}
						/*
						 * if(secondCurrent == null) { continue; }
						 */
						int size = 0;
						// int secondSize = 0;
						String currentLemma = null;
						// String currentSecondLemma = null;
						String[] secondWords = null;
						String[] parts = null;
						//String[] secondParts = null;
						if (c < firstIndex && secondCurrent != null) {
							currentParts = current.split("\\t");

							//TreeMap<String, String> comparisons = new TreeMap<String, String>();
							words = current.split("\\t");
							if (!secondCurrent.equals("")) {
								secondWords = secondCurrent.split("\\t");
								//secondParts = secondWords[0].split("\\+");

							}
							parts = words[0].split("\\+");
							size = 0;
							currentLemma = "";
							if (parts.length == 3) {
								size = paradigms.get(
										parts[1].substring(1).replaceAll("\\|",
												"")).size();// Because of extra
															// | at beginning of
															// word
								currentLemma = parts[1].substring(1);
							} else if (parts.length == 2) {
								size = paradigms.get(
										parts[0].replaceAll("\\|", "")).size();
								currentLemma = parts[0];
							}

							/*
							 * else if(secondParts.length == 3) { size =
							 * secondParadigms
							 * .get(secondParts[1].substring(1).replaceAll
							 * ("\\|", "")).size();//Because of extra | at
							 * beginning of word currentLemma =
							 * secondParts[1].substring(1); } else
							 * if(secondParts.length == 2) { size =
							 * secondParadigms
							 * .get(secondParts[0].replaceAll("\\|",
							 * "")).size(); currentLemma = secondParts[0]; }
							 */
						} else if (c < firstIndex && secondCurrent == null) {
							currentParts = current.split("\\t");

							words = current.split("\\t");
							parts = words[0].split("\\+");
							size = 0;
							currentLemma = "";
							if (parts.length == 3) {
								size = paradigms.get(
										parts[1].substring(1).replaceAll("\\|",
												"")).size();// Because of extra
															// | at beginning of
															// word
								currentLemma = parts[1].substring(1);
							} else if (parts.length == 2) {
								size = paradigms.get(
										parts[0].replaceAll("\\|", "")).size();
								currentLemma = parts[0];
							}
						}

						/*
						 * else if(c >= firstIndex)//Will only happen for second
						 * form (only) predictions { Hashtable<String, String>
						 * comparisons = new Hashtable<String, String>();
						 * if(!secondCurrent.equals("")) { secondWords =
						 * secondCurrent.split("\\t"); secondParts =
						 * secondWords[0].split("\\+"); }
						 * 
						 * if(secondParts.length == 3) { size =
						 * secondParadigms.get
						 * (secondParts[1].substring(1).replaceAll("\\|",
						 * "")).size();//Because of extra | at beginning of word
						 * currentLemma = secondParts[1].substring(1); } else
						 * if(secondParts.length == 2) { size =
						 * secondParadigms.get(secondParts[0].replaceAll("\\|",
						 * "")).size(); currentLemma = secondParts[0]; }
						 * 
						 * }
						 */

						// This part does not need to be doubled: the tag and
						// value will be the same, regardless of the model

						int value = 0;
						String currentTag = "";
						if (parts != null && parts.length == 3) {
							value = tagsInParadigm.get(parts[0].replaceAll(
									"\\|", ""));
							currentTag = parts[0].replaceAll("\\|", "");
						} else if (parts != null && parts.length == 2) {
							value = tagsInParadigm.get(parts[1].replaceAll(
									"\\|", ""));
							currentTag = parts[1].replaceAll("\\|", "");
						}
						/*
						 * else if(secondParts != null && secondParts.length ==
						 * 3) { value =
						 * tagsInParadigm.get(secondParts[0].replaceAll
						 * ("\\|","")); currentTag =
						 * secondParts[0].replaceAll("\\|",""); } else
						 * if(secondParts != null && secondParts.length == 2) {
						 * value =
						 * tagsInParadigm.get(secondParts[1].replaceAll("\\|",
						 * "")); currentTag =
						 * secondParts[1].replaceAll("\\|",""); }
						 */

						int counter = 0;

						Hashtable<Integer, String> featureSet = new Hashtable<Integer, String>();

						// Likewise, we only need to double some parts of this
						// section: we are just making different comparisons
						// We will assume that the "correct" paradigm is the
						// first model
						while (counter < size) {
							String currentForm = null;
							String[] firstParts = null;
							String[] formParts = null;
							String compTag = null;
							if (currentLemma != null) {
								currentForm = paradigms.get(
										currentLemma.replaceAll("\\|", ""))
										.get(counter++);
								firstParts = currentForm.split("\\t");
								if (firstParts.length == 0
										|| firstParts[0].equals("")) {
									continue;
								}
								formParts = firstParts[0].split("\\+");
								compTag = formParts[formParts.length - 1]
										.replaceAll("\\|", "");
							} 
							/* else {
								currentForm = paradigms.get(
										currentLemma.replaceAll("\\|", ""))
										.get(counter++);
								firstParts = currentForm.split("\\t");

								if (firstParts.length == 0
										|| firstParts[0].equals("")) {
									continue;
								}
								formParts = firstParts[0].split("\\+");
								compTag = formParts[formParts.length - 1]
										.replaceAll("\\|", "");
							}
							*/

							if (currentTag.equals(compTag)) {
								continue;
							}
							Integer compValue = tagsInParadigm.get(compTag
									.replaceAll("\\|", ""));
							
							int difference = compValue - value;
							if (difference == 0) {
								continue;
							}

							offset = 3 * (size) * value + compValue * 3 + 1;
							//z++;
							maxIndex = (tagsInParadigm.size())
									* (3 * tagsInParadigm.size());
							features = maxIndex;
							maxIndex *= 2; // To account for separate model
											// features.

							if (useCorpus) {
								maxIndex++;
								corpusIndex = maxIndex;
							}
							if (useAlignmentScore) {
								maxIndex += 2;
								alignmentIndex = maxIndex - 1;
								alignmentIndex2 = maxIndex;
							}
							if (useLM) {
								maxIndex += 1;
								LMIndex = maxIndex;
							}

							if (iterative) {
								maxIndex++;
								rrIndex = maxIndex;
							}
							if (useWord2Vec) {
								w2vOffset = maxIndex;
								maxIndex += vectorSize * size;
							}

							int same = offset;
							int affix = offset + 1;
							int stem = offset + 2;

							int secondSame = features + offset;
							int secondAffix = features + offset + 1;
							int secondStem = features + offset + 2;

							//if (same > maxIndex || affix > maxIndex
							//		|| stem > maxIndex) {
							//	z = 0;
							//}
							// 3 = same, same affix, and same stem
							// size - 1 because we don't compare with a tag with
							// itself

							//ArrayList<String> temp2 = paradigms.get(currentLemma.replaceAll("\\|", ""));
							if (compValue >= paradigms.get(
									currentLemma.replaceAll("\\|", "")).size()) {
								// continue; //This line is for those incomplete
								// paradigms that we can't compare against
							}
							String[] predictionParts = paradigms
									.get(currentLemma.replaceAll("\\|", ""))
									.get(compValue).split("\\t");
							if (predictionParts.length == 0)
							{
								continue;
							}
							if (predictionParts[0].equals("")) {
								continue;
							}
							int paradigmSuffixIndex = predictionParts[1]
									.substring(0,
											predictionParts[1].length() - 1)
									.lastIndexOf("|");
							int suffixIndex = 0;

							//String[] plusSet = currentParts[1].split("\\|");

							if (currentParts != null) {
								suffixIndex = currentParts[1].substring(0,
										currentParts[1].length() - 1)
										.lastIndexOf("|");
							}
							int secondSuffixIndex = 0;
							if (secondWords != null) {
								secondSuffixIndex = secondWords[1].substring(0,
										secondWords[1].length() - 1)
										.lastIndexOf("|");
							}
							int prefixIndex = 0;
							int secondPrefixIndex = 0;
							int paradigmPrefixIndex = 0;
							//if (suffixIndex < 0) {
							//	z++;
							//}
							String predictionStem = null;
							String predictionSuffix = null;
							//String stemBreakdown = null;
							//String[] stemParts = null;

							if (currentParts != null) {
								predictionStem = currentParts[1].substring(0,
										suffixIndex).replaceAll("\\|", "");
								predictionSuffix = currentParts[1].substring(
										suffixIndex).replaceAll("\\||_", "");
								//stemBreakdown = currentParts[currentParts.length - 1].replaceAll(":", "");
								//stemParts = stemBreakdown.split("\\|");
							}
							String predictionPrefix = "";

							// predictionStem = stemParts[0];
							// predictionSuffix = stemParts[stemParts.length -
							// 1];
							String secondPredictionStem = null;
							String secondPredictionSuffix = null;
							String secondPredictionPrefix = null;

							//String secondStemBreakdown = null;
							//String[] secondStemParts = null;
							if (secondWords != null) {
								secondPredictionStem = secondWords[1]
										.substring(0, secondSuffixIndex)
										.replaceAll("\\|", "");
								secondPredictionSuffix = secondWords[1]
										.substring(secondSuffixIndex)
										.replaceAll("\\||_", "");
								secondPredictionPrefix = "";
								//secondStemBreakdown = secondWords[secondWords.length - 1].replaceAll(":", "");
								//secondStemParts = secondStemBreakdown.split("\\|");
							}
							// secondPredictionStem = secondStemParts[0];
							// secondPredictionSuffix =
							// secondStemParts[secondStemParts.length - 1];

							String paradigmPredictionStem = predictionParts[1]
									.substring(0, paradigmSuffixIndex)
									.replaceAll("\\|", "");
							String paradigmPredictionSuffix = predictionParts[1]
									.substring(paradigmSuffixIndex).replaceAll(
											"\\||_", "");
							String paradigmPredictionPrefix = "";

							if (current.replaceAll("\\||_", "").startsWith(
									currentTag)) {
								if (currentParts != null) {
									prefixIndex = currentParts[1].indexOf("|");
									predictionPrefix = currentParts[1]
											.substring(0, prefixIndex);
								}

								if (secondWords != null) {
									secondPrefixIndex = secondWords[1]
											.indexOf("|");
									secondPredictionPrefix = secondWords[1]
											.substring(0, secondPrefixIndex);
								}
								// predictionPrefix = stemParts[0];
								// predictionStem = stemParts[2];
								// secondPredictionPrefix = secondStemParts[0];
								// secondPredictionStem = secondStemParts[2];
							}
							if (predictionParts[1].replaceAll("\\||_", "")
									.startsWith(compTag)) {
								paradigmPrefixIndex = predictionParts[1]
										.indexOf("|");
							}

							paradigmPredictionStem = predictionParts[1]
									.substring(paradigmPrefixIndex,
											paradigmSuffixIndex).replaceAll(
											"\\|", "");

							paradigmPredictionPrefix = predictionParts[1]
									.substring(0, paradigmPrefixIndex);

							if (currentParts != null) {
								predictionStem = currentParts[1].substring(
										prefixIndex, suffixIndex).replaceAll(
										"\\|", "");
								predictionPrefix = predictionPrefix.replaceAll(
										"\\||_", "");
								predictionSuffix = predictionSuffix.replaceAll(
										"\\||_", "");
							}
							if (secondWords != null) {
								secondPredictionStem = secondWords[1]
										.substring(secondPrefixIndex,
												secondSuffixIndex).replaceAll(
												"\\|", "");
								secondPredictionPrefix = secondPredictionPrefix
										.replaceAll("\\||_", "");
								secondPredictionSuffix = secondPredictionSuffix
										.replaceAll("\\||_", "");
							}

							paradigmPredictionPrefix = paradigmPredictionPrefix
									.replaceAll("\\||_", "");
							paradigmPredictionSuffix = paradigmPredictionSuffix
									.replaceAll("\\||_", "");

							if (prefixIndex != 0) {
								if (currentParts != null
										&& paradigmPredictionPrefix.replaceAll(
												"_", "").equals(
												predictionPrefix.replaceAll(
														"_", ""))
										&& paradigmPredictionSuffix.replaceAll(
												"_", "").equals(
												predictionSuffix.replaceAll(
														"_", ""))) {
									featureSet.put(affix, "1.0");
								}
								if (secondWords != null
										&& paradigmPredictionPrefix.replaceAll(
												"_", "").equals(
												secondPredictionPrefix
														.replaceAll("_", ""))
										&& paradigmPredictionSuffix.replaceAll(
												"_", "").equals(
												secondPredictionSuffix
														.replaceAll("_", ""))) {
									featureSet.put(secondAffix, "1.0");
								}
							} else {
								if (currentParts != null
										&& paradigmPredictionSuffix.replaceAll(
												"_", "").equals(
												predictionSuffix.replaceAll(
														"_", ""))) {
									featureSet.put(affix, "1.0");
								}

								if (secondWords != null
										&& paradigmPredictionSuffix.replaceAll(
												"_", "").equals(
												secondPredictionSuffix
														.replaceAll("_", ""))) {
									featureSet.put(secondAffix, "1.0");
								}
							}

							if (currentParts != null
									&& predictionParts[1].replaceAll("\\||_",
											"").equals(
											currentParts[1].replaceAll("\\||_",
													""))) {
								featureSet.put(same, "1.0");
							}

							if (secondWords != null
									&& predictionParts[1].replaceAll("\\||_",
											"").equals(
											secondWords[1].replaceAll("\\||_",
													""))) {
								featureSet.put(secondSame, "1.0");
							}

							if (currentParts != null
									&& paradigmPredictionStem.replaceAll(
											"\\||_", "").equals(
											predictionStem.replaceAll("\\||_",
													""))) {
								featureSet.put(stem, "1.0");
							}

							if (secondWords != null
									&& paradigmPredictionStem.replaceAll(
											"\\||_", "").equals(
											secondPredictionStem.replaceAll(
													"\\||_", ""))) {
								featureSet.put(secondStem, "1.0");
							}

							/*
							 * if(currentLemma.replaceAll("\\||_",
							 * "").equals("atmen") && currentTag.contains("LV"))
							 * { System.out.println(predictionStem);
							 * System.out.println(paradigmPredictionStem);
							 * System.out.println(secondPredictionStem);
							 * System.out
							 * .println(Integer.toString(prefixIndex));
							 * System.out.println(current);
							 * System.out.println(compTag);
							 * 
							 * }
							 */
							//z++;

						}

						if (useCorpus) {
							if (useAlignmentScore) {
								if (counts.containsKey(words[1].replaceAll(
										"\\||_", ""))) {
									featureSet.put(corpusIndex, "1.0");
								}
							}

						}

						if (useAlignmentScore) {
							/*
							 * String [] tempWords =
							 * predictionList.get(c).split("\\t");
							 * if(tempWords.length < 3) { for(int x = 0; x <
							 * predictionList.size(); x++) {
							 * System.out.println(predictionList.get(c)) }
							 * //System.out.println(currentLine.equals(""));
							 * //System.out.println(currentLine); }
							 * if(tempWords[2].equals("1")) { maxScore =
							 * tempWords[3]; }
							 */
							// System.out.println("Original:" +
							// Double.toString(realScore));
							// realScore = 1 / (1 + Math.exp(-0.01 *
							// realScore)); // take sigmoid, to normalise in
							// [0,1]
							// System.out.println("Sigmoid:" +
							// Double.toString(realScore));
							if (currentParts != null) {
								if (c >= firstIndex) {
									System.out.println(currentParts);  //TODO: more descriptive
								}
								Double realScore = predictionScores.get(c);
								featureSet.put(alignmentIndex,
										Double.toString(realScore));
							}
							if (secondWords != null) {
								Double secondScore = Double
										.parseDouble(secondWords[3]);
								featureSet.put(alignmentIndex2,
										Double.toString(secondScore));
							}

						}

						if (useLM) {
							String currentPrediction = predictionList.get(c)
									.split("\\t")[1].replaceAll("\\||_", "");
							Double LMScore = 0.0;
							if (currentParts != null) {
								LMScore = LM.get(currentPrediction);
							} else if (secondWords != null) {
								LMScore = secondLM.get(currentPrediction);
							}
							// LMScore /= currentPrediction.length();
							// LMScore -= Math.log(currentPrediction.length());
							// LMScore = Math.exp(LMScore);

							// LMScore = 1 / (1 + Math.exp(-0.01 * LMScore)); //
							// take sigmoid, to normalise in [0,1]
							// LMScore = Math.exp(LMScore);
							
							featureSet.put(LMIndex, Double.toString(LMScore));
							// featureSet.put(LMIndex2,
							// Double.toString(secondLMScore));

						}
						if (iterative) {
							String currentPrediction = predictionList.get(c)
									.split("\\t")[0].replaceAll("\\||_", "")
									+ predictionList.get(c).split("\\t")[1]
											.replaceAll("\\||_", "");

							if (rrScores.get(currentPrediction) == null) {
								System.out.println(currentPrediction);
							}
							featureSet.put(rrIndex, Double.toString(rrScores
									.get(currentPrediction)));

						}

						if (useWord2Vec) {
							String currentPrediction = predictionList.get(c)
									.split("\\t")[1].replaceAll("\\||_", "");
							// Need to use difference with base instead of
							// straight vector

							String baseScores = w2vScores.get(currentLemma);

							if (baseScores == null) {
								baseScores = oovVector;
							}
							// Need to normalise?
							if (w2vScores.get(currentPrediction) == null) {
								// No need to normalise oov vector; already normalised
								int secondOffset = (value - 1) * vectorSize;
								String w2vValues = oovVector;
								String[] values = w2vValues.split(" ");
								//String[] baseValues = baseScores.split(" ");

								for (int i = 1; i < values.length; i++) {
									featureSet
											.put(w2vOffset + secondOffset + i,
													Double.toString(Double
															.parseDouble(values[i]) /*- Double.parseDouble(baseValues[i])*/));
								}
							} else {
								// need to normalise this vector
								int secondOffset = (value - 1) * vectorSize;
								String w2vValues = w2vScores
										.get(currentPrediction);
								String[] values = w2vValues.split(" ");
								//String[] baseValues = baseScores.split(" ");
								Double normalizer = 0.0;

								for (int i = 1; i < values.length; i++) {
									normalizer += Math
											.pow((Double.parseDouble(values[i]) /*- Double.parseDouble(baseValues[i])*/),
													2);
								}
								normalizer = Math.sqrt(normalizer);

								if (normalizer != 0) {
									for (int i = 1; i < values.length; i++) {
										featureSet
												.put(w2vOffset + secondOffset
														+ i,
														Double.toString((Double
																.parseDouble(values[i]) /*- Double.parseDouble(baseValues[i])*/)
																/ normalizer));
									}
								}

							}

						}
						featureSet.put(-1, Integer.toString(c));
						featureLine.add(featureSet);
					}
				}

				Double randomValue = 1.0;
				if (goldFormIndex == 0) {  //matched on best
					randomValue = generator.nextDouble();
				}
				for (int i = 0; i < featureLine.size(); i++) {
					if (!test) {
						Hashtable<Integer, String> A = featureLine.get(i);
						A.remove(-1);

						for (int j = i + 1; j < featureLine.size(); j++) {

							Hashtable<Integer, String> B = featureLine.get(j);
							B.remove(-1);
							TreeMap<Integer, Double> comparison = new TreeMap<Integer, Double>();
							if ((goldFormIndex == i || goldFormIndex == j)) {
								for (Integer currentKey : A.keySet()) {
									if (useAlignmentScore) {
										if (currentKey > (6 * tagsInParadigm
												.size() * tagsInParadigm.size())) {
											if (B.get(currentKey) == null) {
												comparison
														.put(currentKey,
																Double.parseDouble(A
																		.get(currentKey)));
											}

											else {
												if (Double.parseDouble(A
														.get(currentKey))
														- Double.parseDouble(B
																.get(currentKey)) != 0.0) {
													comparison
															.put(currentKey,
																	Double.parseDouble(A
																			.get(currentKey))
																			- Double.parseDouble(B
																					.get(currentKey)));
												}
											}

											
										}

										else {
											if (B.get(currentKey) == null) {
												comparison.put(currentKey, 1.0);
											}
										}
									}

									else {
										if (B.get(currentKey) == null) {
											comparison.put(currentKey, 1.0);
										}
									}
								}

								for (Integer currentKey : B.keySet()) {
									if (A.get(currentKey) == null) {
										comparison.put(currentKey, -1.0);
									}

									if (useAlignmentScore) {
										if (currentKey > (6 * tagsInParadigm
												.size() * tagsInParadigm.size())) {
											if (A.get(currentKey) == null) {
												comparison
														.put(currentKey,
																0.0 - Double
																		.parseDouble(B
																				.get(currentKey)));
											}

											
										} else {
											if (A.get(currentKey) == null) {
												comparison
														.put(currentKey, -1.0);
											}

										}
									} else {
										if (A.get(currentKey) == null) {
											comparison.put(currentKey, -1.0);
										}

									}
								}
								/*
								 * if(useDirecTLScore) {
								 * comparison.put((contextFeatures.size() +
								 * markovFeatures.size() + chainFeatures.size()
								 * + jointFeatures.size()) *
								 * tagsInParadigm.size() * tagsInParadigm.size()
								 * + tagsInParadigm.size() *
								 * tagsInParadigm.size() + 3,
								 * (predictionScores.get(i)) -
								 * (predictionScores.get(j))); } else
								 * if(!useDirecTLScore) {
								 * comparison.put((contextFeatures.size() +
								 * markovFeatures.size() + chainFeatures.size()
								 * + jointFeatures.size()) *
								 * tagsInParadigm.size() * tagsInParadigm.size()
								 * + tagsInParadigm.size() *
								 * tagsInParadigm.size() + 3, 0.0); }
								 */

								if (!comparison.containsKey(maxIndex)) {
									comparison.put(maxIndex, 0.0);
								}

								//ListComparator bvc = new ListComparator(comparison);
								TreeMap<Integer, Double> sortedMap = comparison;
								//sortedMap.putAll(comparison);

								if (i == goldFormIndex) {

									if (randomValue >= 0) {
										output.write("+1 ");
									}
								} else if (j == goldFormIndex) {

									if (randomValue >= 0) {
										output.write("-1 ");
									}

								} else {
									continue;
								}
								// output.write("qid:" + Integer.toString(qid) +
								// " ");
								String outputLine = "";
								//if (sortedMap.size() == 0) {
								//	int po = 0;
								//}
								Integer value = -1;
								for (Integer current : sortedMap.keySet()) {
									if (current == value) {
										continue;
									}

									if (current > maxIndex) {
										
									}
									outputLine += Integer.toString(current)
											+ ":"
											+ Double.toString(comparison
													.get(current)) + " ";
									value = current;
								}
								/*
								 * if(useDirecTLScore) { outputLine +=
								 * Integer.toString(features.size() *
								 * tagsInParadigm.size() * tagsInParadigm.size()
								 * + 1) + ":" +
								 * Double.toString(predictionScores.get(i)) +
								 * " "; }
								 */
								//String[] parts = words[0].split("\\+");
								if (randomValue >= 0) {
									output.write(outputLine.trim() + "\n");
								}
							} else {
								continue;
							}
						}
					}
					//testing
					else{
						TreeMap<Integer, Double> comparison = new TreeMap<Integer, Double>();
						String index = featureLine.get(i).get(-1);
						for (Integer currentKey : featureLine.get(i).keySet()) {
							if (currentKey < 0) {
								continue;
							}
							if (useAlignmentScore) {
								if (currentKey > (6 * tagsInParadigm.size() * tagsInParadigm
										.size())) {
									if (Double.parseDouble(featureLine.get(i)
											.get(currentKey)) != 0.0) {
										comparison.put(currentKey, Double
												.parseDouble(featureLine.get(i)
														.get(currentKey)));
									}
								} else {
									comparison.put(currentKey, 1.0);
								}
							} else {
								comparison.put(currentKey, 1.0);
							}
						}

						//ListComparator bvc = new ListComparator(comparison);
						TreeMap<Integer, Double> sortedMap = comparison;
						//sortedMap.putAll(comparison);
						String outputLine = "";
						Integer value = -1;
						for (Integer current : sortedMap.keySet()) {
							if (current == value) {
								continue;
							}
							outputLine += Integer.toString(current) + ":"
									+ Double.toString(comparison.get(current))
									+ " ";
							value = current;
						}

						//String[] parts = words[0].split("\\+");

						// int value = tagsInParadigm.get(parts[0]);
						// offset = features.size() * tagsInParadigm.size();
						// outputLine += Integer.toString(offset + 1 + value) +
						// ":1.0";

						// output.write("qid:" + Integer.toString(qid) + " ");
						if (i == goldFormIndex) {
							output.write("1 ");
						} else {
							output.write("2 ");
						}

						/*
						 * if(useDirecTLScore) { //outputLine +=
						 * Integer.toString((contextFeatures.size() +
						 * markovFeatures.size() + chainFeatures.size() +
						 * jointFeatures.size()) * tagsInParadigm.size() *
						 * tagsInParadigm.size() + 1) + ":" +
						 * Double.toString(predictionScores.get(0) -
						 * predictionScores.get(i)) + " "; outputLine +=
						 * Integer.toString((contextFeatures.size() +
						 * markovFeatures.size() + chainFeatures.size() +
						 * jointFeatures.size()) * tagsInParadigm.size() *
						 * tagsInParadigm.size() + tagsInParadigm.size() *
						 * tagsInParadigm.size() + 3) + ":" +
						 * Double.toString(predictionScores.get(i)) + " ";
						 * 
						 * } else if(!useDirecTLScore) { outputLine +=
						 * Integer.toString((contextFeatures.size() +
						 * markovFeatures.size() + chainFeatures.size() +
						 * jointFeatures.size()) * tagsInParadigm.size() *
						 * tagsInParadigm.size() + 3) + ":0 "; }
						 */
						output.write("qid:" + Integer.toString(qid) + " "
								+ outputLine.trim() + " # "
								+ predictionList.get(Integer.parseInt(index))
								+ "\n");
					}

				}

			}

			predictionInput.close();
			paradigmInput.close();
			goldInput.close();
			tagInput.close();
			output.close();

		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
}