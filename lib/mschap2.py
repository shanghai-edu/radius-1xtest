"""
	Microsoft CHAP authentication, version 2
	
	This code is based on the pseudocode from RFC 2759.
	
	We since we only deal with Authentication type requests
	only those methods involved in Access-Request messages
	are implemented
	
	Reverse engineered for Python based on jradius's
	implementation in Java
	
	@author: lee(at)shinatama(dot)homelinux(dot)net
"""
# encoding=utf8
from Crypto.Hash import MD4, SHA
from Crypto.Cipher import DES
from random import randrange
from binascii import hexlify
#from string import upper

class MSCHAP2:
	def __init__(self):
		pass

	"""
		@summary: generates the content for the MS-CHAP2-Response attribute for
			authentication purposes
		@param authChallenge: a 16 byte string consisting of random characters
		@type authChallenge: character string
		@param username: the contents of the User-Name attribute
		@type username: character string
		@param password: the clear-text password for the user
		@type password: character string
		@return: byte string of the encoded MS-CHAP2-Response attribute
		@rtype: string
		@note: The assembly of the MS-CHAP2-RESPONSE attribute has been taken
			from the jradius implementation which conducts the assembly like so:
				2-octets : Flags (where Flags = 0x00)
			   16 octets : Peer-Challenge
				8 octets : Reserved (where Reserved = 0x00)
			   24 octets : NT-Response
			This is different from the RFC which appears to have the Flags at
			the end of the field
	"""
	#def addAttrs(self, authChallenge, username, password):
	def getAuthAttrs(self, username, password):
		response = ""
		#peerChallenge = "0123456789123456"
		authChallenge = ""
		for x in range(0,16):
			authChallenge += chr(randrange(0, 256))
		peerChallenge = ""
		for x in range(0,16):
			peerChallenge += chr(randrange(0, 256))
		ntResponse = self._GenerateNTResponse(authChallenge, peerChallenge, username, password)
		for x in range (0, 2):
			response += '\x00'
		response += peerChallenge
		for x in range(0, 8):
			response += '\x00'
		response += ntResponse
		#print "[DEBUG] [generate] value response: %s" % upper(hexlify(response))
		returnAttrs= {}
		returnAttrs["MS-CHAP-Challenge"] = authChallenge
		returnAttrs["MS-CHAP2-Response"] = response
		return returnAttrs
	
	"""
		@summary: checks an inbound MS-CHAP2-Response attribute to verify the NtResponse 
			should the it be the same as byte 26 onwards
		@param challenge: the contents of the MS-CHAP-Challenge attribute
		@type challenge: byte string
		@param response: the contents of the MS-CHAP2-Response attribute
		@type response: byte string
		@param username: the contents of the User-Name attribute
		@type username: string
		@param password: the original clear-text password for the User-Name attribute
		@return: true if the password is correct, false otherwise
		@rtype: boolean
		@note: The assembly of the MS-CHAP2-RESPONSE attribute has been taken
			from the jradius implementation which conducts the assembly like so:
				2-octets : Flags (where Flags = 0x00)
			   16 octets : Peer-Challenge
				8 octets : Reserved (where Reserved = 0x00)
			   24 octets : NT-Response
			This is different from the RFC which appears to have the Flags at
			the end of the field
	"""
	# commented out as this is not required for Access-Request only processing
	#def checkAuthAttrs(self, challenge, response, username, password):
	#	peerChallenge = response[2:16]
	#	sentNtResponse = response[26:]
	#	ntResponse = self._GenerateNTResponse(self, challenge, peerChallenge, username, password)
	#	return ntResponse == sentNtResponse
	
	"""
	8.1.  GenerateNTResponse()
	
	   GenerateNTResponse(
	   IN  16-octet              AuthenticatorChallenge,
	   IN  16-octet              PeerChallenge,
	   IN  0-to-256-char         UserName,
	   IN  0-to-256-unicode-char Password,
	   OUT 24-octet              Response )
	   {
	      8-octet  Challenge
	      16-octet PasswordHash
	
	      ChallengeHash( PeerChallenge, AuthenticatorChallenge, UserName,
	                     giving Challenge)
	
	      NtPasswordHash( Password, giving PasswordHash )
	      ChallengeResponse( Challenge, PasswordHash, giving Response )
	   }
	"""
	def _GenerateNTResponse(self, AuthenticatorChallenge, PeerChallenge, UserName, Password):
		challenge = self._ChallengeHash(PeerChallenge, AuthenticatorChallenge, UserName)
		pwHash = self._NtPasswordHash(Password)
		response = self._ChallengeResponse(challenge, pwHash)
		return response
	
	"""
	8.2.  ChallengeHash()
	
	   ChallengeHash(
	   IN 16-octet               PeerChallenge,
	   IN 16-octet               AuthenticatorChallenge,
	   IN  0-to-256-char         UserName,
	   OUT 8-octet               Challenge
	   {
	
	      /*
	       * SHAInit(), SHAUpdate() and SHAFinal() functions are an
	       * implementation of Secure Hash Algorithm (SHA-1) [11]. These are
	       * available in public domain or can be licensed from
	       * RSA Data Security, Inc.
	       */
	
	      SHAInit(Context)
	      SHAUpdate(Context, PeerChallenge, 16)
	      SHAUpdate(Context, AuthenticatorChallenge, 16)
	
	      /*
	       * Only the user name (as presented by the peer and
	       * excluding any prepended domain name)
	       * is used as input to SHAUpdate().
	       */
	
	      SHAUpdate(Context, UserName, strlen(Username))
	      SHAFinal(Context, Digest)
	      memcpy(Challenge, Digest, 8)
	   }
	"""
	def _ChallengeHash(self, PeerChallenge, AuthenticatorChallenge, UserName):
		challenge = SHA.new(PeerChallenge + AuthenticatorChallenge + UserName).digest()
		#print "[DEBUG] [_ChallengeHash] challenge: " % upper(hexlify(challenge[0:8]))
		return challenge[0:8]
	
	"""
	8.3.  NtPasswordHash()
	
	   NtPasswordHash(
	   IN  0-to-256-unicode-char Password,
	   OUT 16-octet              PasswordHash )
	   {
	      /*
	       * Use the MD4 algorithm [5] to irreversibly hash Password
	       * into PasswordHash.  Only the password is hashed without
	       * including any terminating 0.
	       */
	   }
	"""
	def _NtPasswordHash(self, Password):
		unicodePw = Password.encode("utf-16-le")
		hashPw = MD4.new(unicodePw).digest()
		#print "[DEBUG] [_NtPasswordHash] hashPw: %s" % upper(hexlify(hashPw[0:17]))
		return hashPw[0:17]
	
	"""
	8.5.  ChallengeResponse()
	
	   ChallengeResponse(
	   IN  8-octet  Challenge,
	   IN  16-octet PasswordHash,
	   OUT 24-octet Response )
	   {
	      Set ZPasswordHash to PasswordHash zero-padded to 21 octets
	
	      DesEncrypt( Challenge,
	                  1st 7-octets of ZPasswordHash,
	                  giving 1st 8-octets of Response )
	
	      DesEncrypt( Challenge,
	                  2nd 7-octets of ZPasswordHash,
	                  giving 2nd 8-octets of Response )
	
	      DesEncrypt( Challenge,
	                  3rd 7-octets of ZPasswordHash,
	                  giving 3rd 8-octets of Response )
	   }
	"""
	def _ChallengeResponse(self, challenge, pwhash):
		zPwHash = pwhash
		# for some reason in python we need to pad an extra byte so that
		# the offset works out correctly when we call DesEncrypt
		zPwHash += '\x00' * (22 - len(pwhash))
		response = ""
		#print "[DEBUG] zPwHash: %s" % upper(hexlify(zPwHash))
		for x in range(0, 3):
			offset = x * 7
			response += self._DesEncrypt(challenge, zPwHash, offset)
		return response
	
	"""
	8.6.  DesEncrypt()
	
	   DesEncrypt(
	   IN  8-octet Clear,
	   IN  7-octet Key,
	   OUT 8-octet Cypher )
	   {
	      /*
	       * Use the DES encryption algorithm [4] in ECB mode [10]
	       * to encrypt Clear into Cypher such that Cypher can
	       * only be decrypted back to Clear by providing Key.
	       * Note that the DES algorithm takes as input a 64-bit
	       * stream where the 8th, 16th, 24th, etc.  bits are
	       * parity bits ignored by the encrypting algorithm.
	       * Unless you write your own DES to accept 56-bit input
	       * without parity, you will need to insert the parity bits
	       * yourself.
	       */
	   }
	   
	   This implementation was interpreted into python based on source
	   code from jradius net.jradius.util.MSCHAP.Class#parity_key
	   
	   Turns a 7 octet key cut up from the NtPasswordHash into an
	   8 octect key as required by DES(ECB) encryption
	"""
	def _DesEncrypt(self, clear, key, offset):
		cNext = 0
		cWorking = 0
		hexKey = {}
		#print "[DEBUG] [_56bitkey] key: %s offset: %d len(key): %d" % (hexlify(key), offset, len(key))
		for x in range(0,8):
			cWorking = 0xFF & int(hexlify(key[x + offset]),16)
			hexKey[x] = ((cWorking >> x) | cNext | 1) & 0xFF
			#print "[DEBUG] [_56bitKey] newKey[x]: %s x: %d" % (hex(hexKey[x]),x)
			cWorking = 0xFF & int(hexlify(key[x + offset]),16) 
			cNext = ((cWorking << (7 - x)))
		#print "[DEBUG] [_56bitKey] hexKey: %s" % hexKey
		newKey = ""
		for x in range(0,len(hexKey)):
			#print "[DEBUG] [_56bitKey] hex(hexKey[x]): %s" % hex(hexKey[x])
			newKey += chr(int(hexKey[x]))
		#print "[DEBUG] [_56bitKey] newKey: %s" % hexlify(newKey)
		des = DES.new(newKey, DES.MODE_ECB)
		return des.encrypt(clear)
