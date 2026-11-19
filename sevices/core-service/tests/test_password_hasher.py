from app.security.password_hasher import BcryptPasswordHasher

SEED_HASH = "$2b$12$iEXK.LbXepaIua5Qjsu9kuCarJxDSFrt.ICgKO2y2nhJn6cWcMq/G"


def test_bcrypt_hash_and_verify_roundtrip():
    h = BcryptPasswordHasher(rounds=4)
    hashed = h.hash("Senha@123")
    assert hashed.startswith("$2b$") and hashed != "Senha@123"
    assert h.verify("Senha@123", hashed)
    assert not h.verify("Outra@123", hashed)


def test_seed_user_password_is_senha_123():
    """database/seed.sql documenta 'Senha: Senha@123' para o Dr. Fulano."""
    assert BcryptPasswordHasher().verify("Senha@123", SEED_HASH)


def test_malformed_hash_is_just_a_wrong_password():
    assert not BcryptPasswordHasher().verify("Senha@123", "nao-e-bcrypt")


def test_password_longer_than_72_bytes_does_not_crash():
    h = BcryptPasswordHasher(rounds=4)
    long_pw = "A1@" + "x" * 100
    assert h.verify(long_pw, h.hash(long_pw))
