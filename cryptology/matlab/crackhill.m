function [plaintext]=crackhill(snippetplaintext,ciphertext,blocklength)
bl = blocklength;
cText = ciphertext;
intText = cText - 97;
lenCT = length(intText);
colCT = ceil(lenCT/bl);
pad = bl*colCT - lenCT;
if pad > 0
    lenCT = lenCT + pad;
    padding = zeros(1,pad);
    intText = [intText padding];
end
blocks = reshape(intText, [bl, colCT]); %round up number of columns

known = snippetplaintext;
intKnown = known - 97;
lenK = length(intKnown);
colK = ceil(lenK/bl);
pad = bl*colK - lenK;
if pad > 0
    lenK = lenK + pad;
    padding = zeros(1,pad);
    intKnown = [intKnown padding];
end
knownBlocks = reshape(intKnown, [bl, colK]);
cStart = blocks(:, 1:bl); %take square chunk of cipher text

sSize = bl^2; %number of characters in each sample
pLeft = lenK - sSize;
pSample = zeros(bl); 
%get key using known
keyInv = [];
for i=1:pLeft
    try
        pText = intKnown(i:(i+sSize-1));
        pSample = reshape(pText, [bl, bl]); %make square chunk of known text
        d = round(det(pSample));
        recipd = powermod(d,-1,26); %assuming normal alphabet
        plainInv = recipd*det(pSample)*inv(pSample);
        plainInv = round(plainInv);
        plainInv = mod(plainInv,26);
        key = mod(cStart*plainInv, 26);
        %get key inverse for decryption
        d = round(det(key));
        recipd = powermod(d,-1,26); %will display 'No inverse' if failed
        keyInv = recipd*det(key)*inv(key);
        keyInv = round(keyInv);
        keyInv = mod(keyInv, 26);
        break;
    catch ME
        if (strcmp(ME.identifier,'MATLAB:catenate:dimensionMismatch'))
            %no inverse for d, iterate
        end
    end
end
if isempty(keyInv)
    %try something else
    plaintext = 'could not decrypt';
else
    deciphered = mod(keyInv*blocks,26);
    deciphered = reshape(deciphered, [1 lenCT]);
    deciphered = deciphered + 97;
    plaintext = char(deciphered);
end
end
